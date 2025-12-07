# Claude Code Telegram Notification Plugin

A context-aware notification plugin for Claude Code that sends messages via Telegram Bot API. Perfect for monitoring Claude Code task status when working remotely or away from your computer.

[中文文档](README_CN.md)

## Features

- Remote Monitoring - Push notifications to your phone when tasks complete or need confirmation
- Zero Dependencies - Uses only Node.js built-in modules
- Secure Configuration - Supports environment variables for Token configuration
- Context Aware - Automatically extracts project name and task status

## Installation

### Method 1: Local Marketplace Installation (Recommended)

1. Create a local marketplace directory structure:

```bash
# Create marketplace anywhere
mkdir -p ~/claude-marketplace/.claude-plugin

# Create marketplace manifest
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

2. Copy notify-tg directory to the marketplace:

```bash
cp -r /path/to/notify-tg ~/claude-marketplace/
```

3. Add marketplace and install in Claude Code:

```bash
# Launch Claude Code
claude

# Add local marketplace
/plugin marketplace add ~/claude-marketplace

# Install plugin
/plugin install notify-tg@local-marketplace
```

4. Restart Claude Code for the plugin to take effect.

### Method 2: Direct Configuration

Merge hooks configuration into `~/.claude/settings.json`:

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

> Note: Replace `/path/to/notify-tg` with the actual path.

## Configuration (Required)

You need to provide a Telegram Bot Token and Chat ID.

### Method 1: Environment Variables (Recommended)

Add to your shell configuration file (`.bashrc`, `.zshrc`):

```bash
export TELEGRAM_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="987654321"
```

### Method 2: Configuration File

Edit `config/notify-config.json`:

```json
{
  "telegram": {
    "token": "YOUR_BOT_TOKEN_HERE",
    "chatId": "YOUR_CHAT_ID_HERE"
  }
}
```

## Monitored Events

The plugin automatically listens for the following events:

| Event | Trigger | Notification Example |
|-------|---------|---------------------|
| Stop | Claude completes a task | ✅ Claude Response Complete - [Project] |
| Notification | Authorization or confirmation needed | ⚠️ Claude Needs Attention - [Project] - [Message] |

## Testing

Manually run the script to test your configuration:

```bash
# Test Stop event
echo '{"hook_event_name":"Stop","cwd":"/path/to/project"}' | node scripts/notify-hook.js

# Test Notification event
echo '{"hook_event_name":"Notification","cwd":"/path/to/project","notification_type":"PermissionRequest","message":"Permission required"}' | node scripts/notify-hook.js
```

## File Structure

```
notify-tg/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── hooks/
│   └── hooks.json           # Hook configuration
├── scripts/
│   └── notify-hook.js       # Core script
├── config/
│   └── notify-config.json   # Configuration file
├── README.md                # English documentation
└── README_CN.md             # Chinese documentation
```

## License

Apache License 2.0
