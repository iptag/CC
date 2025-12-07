const fs = require('fs');
const https = require('https');
const path = require('path');

// --- 配置与工具 ---

// 简单的日志记录
function log(msg) {
  // 在实际插件运行中，stdout 可能会被 Claude 捕获，但在调试时很有用
  // process.stderr.write(`[Notify-TG] ${msg}\n`);
}

// 读取配置文件
function loadConfig() {
  try {
    const configPath = path.join(__dirname, '../config/notify-config.json');
    if (fs.existsSync(configPath)) {
      return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    }
  } catch (e) {
    log('无法读取配置文件: ' + e.message);
  }
  return {};
}

// 替换模板变量
function escapeMarkdown(text) {
  if (!text) return '';
  return text.replace(/([_*`\[\]\\])/g, '\\$1');
}

function formatMessage(template, data) {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : match;
  });
}

// 发送 Telegram 消息
function sendTelegramMessage(token, chatId, text) {
  if (!token || !chatId || !text) {
    log('缺少必要参数 (Token, ChatID 或 Message)，无法发送。');
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      chat_id: chatId,
      text: text,
      parse_mode: 'Markdown'
    });

    const options = {
      hostname: 'api.telegram.org',
      port: 443,
      path: `/bot${token}/sendMessage`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    const req = https.request(options, (res) => {
      res.resume();
      res.on('end', () => resolve());
      if (res.statusCode >= 200 && res.statusCode < 300) {
        log('消息发送成功');
      } else {
        log(`发送失败，状态码: ${res.statusCode}`);
      }
    });

    req.on('error', (e) => {
      log(`网络错误: ${e.message}`);
      reject(e);
    });

    req.write(data);
    req.end();
  });
}

// --- 主逻辑 ---

const main = () => {
  // 1. 读取并解析 Hook 输入 (Stdin)
  let inputData = '';
  
  // 设置超时，避免 Stdin 阻塞过久
  const stdinTimeout = setTimeout(() => {
    log('等待输入超时');
    process.exit(1);
  }, 15000);

  process.stdin.on('data', chunk => {
    inputData += chunk;
  });

  process.stdin.on('error', (err) => {
    clearTimeout(stdinTimeout);
    log('Stdin 读取失败: ' + err.message);
    process.exitCode = 1;
  });

  process.stdin.on('end', async () => {
    clearTimeout(stdinTimeout);
    if (!inputData.trim()) return;

    let hookData;
    try {
      hookData = JSON.parse(inputData);
    } catch (e) {
      log('JSON 解析失败: ' + e.message);
      process.exitCode = 1;
      return;
    }

    try {
      await handleHook(hookData);
    } catch (e) {
      log('处理 Hook 失败: ' + e.message);
      process.exitCode = 1;
    }
  });
};

const handleHook = async (hookData) => {
  const config = loadConfig();
  
  // 2. 确定 Token 和 ChatID
  // 优先级: 环境变量 > 配置文件
  const token = process.env.TELEGRAM_TOKEN || (config.telegram && config.telegram.token);
  const chatId = process.env.TELEGRAM_CHAT_ID || (config.telegram && config.telegram.chatId);

  if (!token || !chatId) {
    log('未配置 Telegram Token 或 Chat ID。请设置环境变量或修改 config/notify-config.json。');
    return;
  }

  const eventName = hookData.hook_event_name;
  const eventConfig = config.events && config.events[eventName];

  // 如果事件被禁用或未定义，则忽略
  if (!eventConfig || eventConfig.enabled === false) {
    return;
  }

  // 3. 准备上下文数据
  const cwd = hookData.cwd || process.cwd();
  const projectName = path.basename(cwd);
  const context = {
    projectName: escapeMarkdown(projectName),
    currentDir: cwd,
    sessionId: (hookData.session_id || '').substring(0, 8),
    message: escapeMarkdown(hookData.message || ''),
    notificationType: hookData.notification_type || '',
    eventName: eventName,
    title: eventConfig.title || eventName
  };

  // 4. 生成消息文本
  const hasMessage = Boolean(hookData.message);
  let templateToUse = eventConfig.messageTemplate || eventConfig.fallbackMessage;

  if (eventName === 'Notification') {
    templateToUse = hasMessage
      ? (eventConfig.messageTemplate || eventConfig.fallbackMessage)
      : (eventConfig.fallbackMessage || eventConfig.messageTemplate);
  }

  if (!templateToUse) {
    log('未配置消息模板，跳过发送。');
    return;
  }

  const messageText = formatMessage(templateToUse, context);

  // 5. 发送
  await sendTelegramMessage(token, chatId, messageText);
};

// 启动
main();
