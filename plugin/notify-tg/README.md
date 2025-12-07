# Claude Code Telegram 通知插件

基于 Node.js 的上下文感知通知插件，通过 Telegram Bot API 发送消息。适合在远程工作或离开电脑时监控 Claude Code 任务状态。

## 特性

- 远程监控 - 任务完成或需要确认时推送到手机
- 零依赖 - 仅使用 Node.js 内置模块
- 安全配置 - 支持环境变量配置 Token
- 上下文感知 - 自动提取项目名和任务状态

## 安装

### 方法 1：本地 Marketplace 安装（推荐）

1. 创建本地 marketplace 目录结构：

```bash
# 在任意位置创建 marketplace
mkdir -p ~/claude-marketplace/.claude-plugin

# 创建 marketplace 清单
cat > ~/claude-marketplace/.claude-plugin/marketplace.json << 'EOF'
{
  "name": "local-marketplace",
  "owner": { "name": "local" },
  "plugins": [
    {
      "name": "notify-tg",
      "source": "./notify-tg",
      "description": "Telegram notification plugin"
    }
  ]
}
EOF
```

2. 将 notify-tg 目录复制到 marketplace：

```bash
cp -r /path/to/notify-tg ~/claude-marketplace/
```

3. 在 Claude Code 中添加 marketplace 并安装：

```bash
# 启动 Claude Code
claude

# 添加本地 marketplace
/plugin marketplace add ~/claude-marketplace

# 安装插件
/plugin install notify-tg@local-marketplace
```

4. 重启 Claude Code 使插件生效。

### 方法 2：直接复制到用户配置

将 hooks 配置合并到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node /path/to/notify-tg/scripts/notify-hook.js",
            "timeout": 20
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node /path/to/notify-tg/scripts/notify-hook.js",
            "timeout": 20
          }
        ]
      }
    ]
  }
}
```

> 注意：将 `/path/to/notify-tg` 替换为实际路径。

## 配置（必须）

需要提供 Telegram Bot Token 和 Chat ID。

### 方法 1：环境变量（推荐）

在 shell 配置文件（`.bashrc`、`.zshrc`）中添加：

```bash
export TELEGRAM_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="987654321"
```

### 方法 2：配置文件

编辑 `config/notify-config.json`：

```json
{
  "telegram": {
    "token": "YOUR_BOT_TOKEN_HERE",
    "chatId": "YOUR_CHAT_ID_HERE"
  }
}
```

## 监听事件

插件自动监听以下事件：

| 事件 | 触发时机 | 通知示例 |
|------|---------|---------|
| Stop | Claude 完成任务 | ✅ Claude 响应完成 - [项目名] |
| Notification | 需要授权或确认 | ⚠️ Claude 需要注意 - [项目名] - [消息] |

## 测试

手动运行脚本测试配置：

```bash
# 测试 Stop 事件
echo '{"hook_event_name":"Stop","cwd":"/path/to/project"}' | node scripts/notify-hook.js

# 测试 Notification 事件
echo '{"hook_event_name":"Notification","cwd":"/path/to/project","notification_type":"PermissionRequest","message":"需要权限"}' | node scripts/notify-hook.js
```

## 文件结构

```
notify-tg/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据
├── hooks/
│   └── hooks.json           # Hook 配置
├── scripts/
│   └── notify-hook.js       # 核心脚本
├── config/
│   └── notify-config.json   # 配置文件
└── README.md
```

## 许可证

Apache License 2.0
