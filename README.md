# Claude Code Extensions

Claude Code 扩展集合，包含自定义 Skills 和 Plugins。

## 项目结构

```
myclaude/
├── CLAUDE.md                  # 全局配置参考
├── tg-proxy-auto-del.js       # Telegram 反代 Worker 脚本
├── skills/                    # Agent Skills
│   ├── codex/
│   ├── searching-with-exa/
│   └── jimeng-api/
└── plugin/                    # Plugins
    └── notify-tg/
```

## Skills

### Codex CLI (`skills/codex`)

将复杂代码任务委托给 Codex AI，支持文件引用（`@` 语法）和结构化输出。

**用途**：
- 复杂代码分析
- 大规模重构
- 自动代码生成

**使用**：
```bash
uv run ~/.claude/skills/codex/scripts/codex.py - <<'EOF'
explain @src/main.ts
EOF
```

### 即梦图像生成 (`skills/jimeng-api`)

通过本地部署的即梦 API 生成图片，支持文生图和图生图。

API 服务：https://github.com/iptag/jimeng-api

**用途**：
- 文本生成图片
- 图片风格转换
- 支持多种分辨率（1k/2k/4k）和比例

**使用**：
```bash
python scripts/generate_image.py text "描述内容" --session-id "YOUR_SESSION_ID"
```

### Exa 智能搜索 (`skills/searching-with-exa`)

基于 Exa AI 的智能语义搜索工具，支持深度搜索、代码示例、GitHub 仓库、论文等。

**特性**：
- 智能意图识别（concept/tutorial/example/github/paper/news/research）
- 深度语义搜索（neural/deep 模式）
- 自动内容抓取与摘要
- 类别过滤（GitHub、论文、新闻等）

**示例**：
```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py smart "React hooks best practices"
```

## Plugins

### Telegram 通知 (`plugin/notify-tg`)

任务完成或需要确认时，通过 Telegram 推送通知。

**安装**：详见 [plugin/notify-tg/README.md](plugin/notify-tg/README.md)

### Telegram 反代与消息自动删除 (`tg-proxy-auto-del.js`)

部署在 Cloudflare Workers 上，提供 Telegram API 反向代理，并支持定时自动删除包含特定关键词（如 "Claude"）的消息，防止通知刷屏。

**功能**：
- 提供 Telegram Bot API 反向代理 (解决网络限制)
- 支持鉴权 (`X-TG-Proxy-Key`)
- 自动检测并删除包含特定关键词的消息 (默认延迟 15 分钟)

**手动部署步骤 (Cloudflare Dashboard)**：

1. **创建 Worker**：
   - 登录 Cloudflare Dashboard，进入 Workers & Pages。
   - 点击 "Create Application" -> "Create Worker"。
   - 命名为 `tg-proxy` (或你喜欢的名字)，点击 Deploy。
   - 点击 "Edit code"，将 `tg-proxy-auto-del.js` 的内容完整复制并覆盖默认代码，点击 "Save and deploy"。

2. **配置 KV (键值存储)**：
   - 在 Workers & Pages 主页，点击 "KV" -> "Create a namespace"。
   - 命名为 `TG_MSG_KV`，点击 Add。
   - 回到你的 Worker 设置页面 (`tg-proxy` -> Settings)。
   - 在 **KV Namespace Bindings** 下，点击 "Add binding"。
   - Variable name 填 `TG_MSG_KV`，Namespace 选择刚才创建的 `TG_MSG_KV`。
   - 点击 "Save and deploy"。

3. **配置环境变量**：
   - 在 Worker 设置页面 (`tg-proxy` -> Settings -> Variables)。
   - 在 **Environment Variables** 下，点击 "Add variable"。
   - 添加以下变量：
     - `AUTO_DELETE_KEYWORDS`: 设置为 `Claude` (或用逗号分隔的多个关键词)。
     - `PROXY_KEY`: 设置你的访问密钥 (建议需要鉴权)。
   - 点击 "Save and deploy"。

4. **配置定时任务 (Cron Triggers)**：
   - 在 Worker 设置页面 (`tg-proxy` -> Settings -> Triggers)。
   - 在 **Cron Triggers** 下，点击 "Add Cron Trigger"。
   - 设置 Cron 表达式为 `每分钟执行一次` ，用于检查并删除过期消息。
   - 点击 "Add Trigger"。

5. **使用**：
   将 `notify-tg` 插件的配置 `baseApi` 指向你的 Worker 地址，例如：`https://tg-proxy.你的子域名.workers.dev/bot`

## 配置

`CLAUDE.md` 是 Claude Code 的全局配置文件（默认位于 `~/.claude/CLAUDE.md`），用于定义工作流规则、搜索策略和代码编辑规范。

- **工作流契约**：所有 Codex skill 负责执行编辑。
- **Web 搜索**：默认启用 searching-with-exa + context7 MCP。
- **质量基准**：约束代码风格与输出规范，确保响应一致。

## 安装

### Skills 安装

将 `skills/` 目录复制到 `~/.claude/skills/`：

```bash
cp -r skills/* ~/.claude/skills/
```

### Plugin 安装

参考各 plugin 目录下的 README 文档。

## 许可证

Apache License 2.0
