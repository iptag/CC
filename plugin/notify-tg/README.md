# Claude Code Telegram 通知插件

基于 Node.js 的上下文感知通知插件，通过 Telegram Bot API 发送消息，替代本地系统通知。适合在远程工作或离开电脑时监控 Claude Code 任务状态。

## ✨ 特性

- 📱 **远程监控** - 任务完成或需要确认时，直接推送到你的手机
- 🚀 **零依赖** - 仅使用 Node.js 内置模块 (https, fs, path)
- 🔒 **安全配置** - 支持环境变量配置 Token，避免硬编码
- 🎯 **上下文感知** - 自动提取项目名和任务状态

## 📦 安装说明

### Claude Code Marketplace 安装

*(假设你已经配置了 Marketplace)*

```bash
# 安装插件
/plugin install notify-tg

# 启用插件
/plugin enable notify-tg
```

## ⚙️ 配置 (关键步骤)

为了让插件工作，你需要提供 Telegram Bot Token 和 Chat ID。

### 方法 1: 环境变量 (推荐)

在你的 shell 配置文件 (`.bashrc`, `.zshrc`) 中添加：

```bash
export TELEGRAM_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="987654321"
```

### 方法 2: 配置文件

编辑插件目录下的 `config/notify-config.json`：

```json
{
  "telegram": {
    "token": "YOUR_BOT_TOKEN_HERE",
    "chatId": "YOUR_CHAT_ID_HERE"
  },
  ...
}
```

## 🚀 快速开始

安装并配置后，插件会自动监听以下事件：

1.  **Stop**: 当 Claude 完成一个长任务时。
    *   通知: "✅ Claude 响应完成 - [项目名]"
2.  **Notification**: 当 Claude 需要你授权或确认时。
    *   通知: "⚠️ Claude 需要注意 - [项目名] - [具体消息]"

## 🧪 测试

你可以手动运行脚本来测试配置是否正确：

```bash
# 进入插件目录后执行

# 测试 Stop 事件
echo '{"hook_event_name":"Stop","cwd":"/path/to/my-project"}' | node scripts/notify-hook.js

# 测试 Notification 事件
echo '{"hook_event_name":"Notification","cwd":"/path/to/my-project","notification_type":"PermissionRequest","message":"需要权限执行命令"}' | node scripts/notify-hook.js
```

## 📋 文件结构

```
plugins/notify-tg/
├── hooks/
│   └── hooks.json           # Hook 定义
├── scripts/
│   └── notify-hook.js       # 核心逻辑脚本
├── config/
│   └── notify-config.json   # 配置文件
└── README.md
```

## 📄 许可证

Apache License 2.0
