# Claude Code Extensions

Claude Code 扩展集合，包含自定义 Skills 和 Plugins。

## 项目结构

```
myclaude/
├── CLAUDE.md                  # 全局配置参考（实际配置位于 ~/.claude/CLAUDE.md）
├── skills/                    # Agent Skills
│   ├── codex/                 # Codex CLI 集成
│   │   ├── SKILL.md
│   │   └── scripts/codex.py
│   ├── searching-with-exa/    # Exa 智能搜索
│   │   ├── SKILL.md
│   │   ├── REFERENCE.md
│   │   ├── examples.py
│   │   └── scripts/exa_fetch.py
│   └── jimeng-api/            # 即梦 AI 图像生成
│       ├── Skill.md
│       └── scripts/generate_image.py
└── plugin/                    # Plugins
    └── notify-tg/             # Telegram 通知插件
        ├── .claude-plugin/plugin.json
        ├── hooks/hooks.json
        ├── scripts/notify-hook.js
        └── config/notify-config.json
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
