const fs = require('fs');
const https = require('https');
const path = require('path');

// --- Configuration & Utilities ---

// Simple logging
function log(msg) {
  // In actual plugin runtime, stdout may be captured by Claude, but useful for debugging
  // process.stderr.write(`[Notify-TG] ${msg}\n`);
}

// Load configuration file
function loadConfig() {
  try {
    const configPath = path.join(__dirname, '../config/notify-config.json');
    if (fs.existsSync(configPath)) {
      return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    }
  } catch (e) {
    log('Failed to read config file: ' + e.message);
  }
  return {};
}

// Escape Markdown special characters
function escapeMarkdown(text) {
  if (!text) return '';
  return text.replace(/([_*`\[\]\\])/g, '\\$1');
}

// Replace template variables
function formatMessage(template, data) {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : match;
  });
}

// Send Telegram message
function sendTelegramMessage(token, chatId, text) {
  if (!token || !chatId || !text) {
    log('Missing required parameters (Token, ChatID or Message), cannot send.');
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
        log('Message sent successfully');
      } else {
        log(`Send failed, status code: ${res.statusCode}`);
      }
    });

    req.on('error', (e) => {
      log(`Network error: ${e.message}`);
      reject(e);
    });

    req.write(data);
    req.end();
  });
}

// --- Main Logic ---

const main = () => {
  // 1. Read and parse Hook input (Stdin)
  let inputData = '';

  // Set timeout to avoid Stdin blocking too long
  const stdinTimeout = setTimeout(() => {
    log('Input timeout');
    process.exit(1);
  }, 15000);

  process.stdin.on('data', chunk => {
    inputData += chunk;
  });

  process.stdin.on('error', (err) => {
    clearTimeout(stdinTimeout);
    log('Stdin read failed: ' + err.message);
    process.exitCode = 1;
  });

  process.stdin.on('end', async () => {
    clearTimeout(stdinTimeout);
    if (!inputData.trim()) return;

    let hookData;
    try {
      hookData = JSON.parse(inputData);
    } catch (e) {
      log('JSON parse failed: ' + e.message);
      process.exitCode = 1;
      return;
    }

    try {
      await handleHook(hookData);
    } catch (e) {
      log('Hook processing failed: ' + e.message);
      process.exitCode = 1;
    }
  });
};

const handleHook = async (hookData) => {
  const config = loadConfig();

  // 2. Determine Token and ChatID
  // Priority: Environment variables > Config file
  const token = process.env.TELEGRAM_TOKEN || (config.telegram && config.telegram.token);
  const chatId = process.env.TELEGRAM_CHAT_ID || (config.telegram && config.telegram.chatId);

  if (!token || !chatId) {
    log('Telegram Token or Chat ID not configured. Please set environment variables or modify config/notify-config.json.');
    return;
  }

  const eventName = hookData.hook_event_name;
  const eventConfig = config.events && config.events[eventName];

  // If event is disabled or undefined, ignore
  if (!eventConfig || eventConfig.enabled === false) {
    return;
  }

  // 3. Prepare context data
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

  // 4. Generate message text
  const hasMessage = Boolean(hookData.message);
  let templateToUse = eventConfig.messageTemplate || eventConfig.fallbackMessage;

  if (eventName === 'Notification') {
    templateToUse = hasMessage
      ? (eventConfig.messageTemplate || eventConfig.fallbackMessage)
      : (eventConfig.fallbackMessage || eventConfig.messageTemplate);
  }

  if (!templateToUse) {
    log('Message template not configured, skipping send.');
    return;
  }

  const messageText = formatMessage(templateToUse, context);

  // 5. Send
  await sendTelegramMessage(token, chatId, messageText);
};

// Start
main();
