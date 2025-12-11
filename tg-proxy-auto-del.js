// 目标 Telegram API
const TG_API_ORIGIN = 'https://api.telegram.org';

// 验证用 Header 名称
const AUTH_HEADER_NAME = 'X-TG-Proxy-Key';

// 自动删除的延迟时间 (15分钟)
const DELETE_DELAY_MS = 15 * 60 * 1000; 

function buildCorsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,HEAD,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': '*',
  };
}

function handleOptions() {
  return new Response(null, {
    status: 204,
    headers: buildCorsHeaders(),
  });
}

export default {
  /**
   * Cloudflare Worker HTTP 入口
   */
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 健康检查
    if (url.pathname === '/' || url.pathname === '/healthz') {
      return new Response('Telegram Bot API Proxy with Auto-Delete\n', {
        status: 200,
        headers: { 'Content-Type': 'text/plain; charset=utf-8', ...buildCorsHeaders() },
      });
    }

    // CORS 预检
    if (request.method === 'OPTIONS') {
      return handleOptions();
    }

    // 路径检查
    if (!url.pathname.startsWith('/bot') && !url.pathname.startsWith('/file/bot')) {
      return new Response('Not found', { status: 404, headers: buildCorsHeaders() });
    }

    // 鉴权
    const expectedKey = env.PROXY_KEY;
    if (expectedKey) {
      const clientKey = request.headers.get(AUTH_HEADER_NAME);
      if (!clientKey || clientKey !== expectedKey) {
        return new Response('Unauthorized', { status: 401, headers: buildCorsHeaders() });
      }
    }

    // ==============
    // 拦截逻辑：检查是否包含 关键词
    // ==============
    let monitorDeletion = false;
    let requestClone = null;
    
    // 获取用户配置的关键词，按逗号分割并去除空格
    const keywordsStr = env.AUTO_DELETE_KEYWORDS || '';
    const keywords = keywordsStr.split(',').map(k => k.trim()).filter(k => k.length > 0);

    // 只有配置了关键词且是 POST 请求才进行检查
    if (keywords.length > 0 && request.method === 'POST') {
      try {
        // 克隆请求以读取 Body
        requestClone = request.clone();
        const contentType = request.headers.get('content-type') || '';
        
        if (contentType.includes('application/json')) {
          const bodyJson = await requestClone.json();
          // 检查 text (sendMessage) 或 caption (sendPhoto/Video/Document)
          const content = bodyJson.text || bodyJson.caption || '';
          
          // 检查是否包含任意一个关键词
          if (content && keywords.some(keyword => content.includes(keyword))) {
            monitorDeletion = true;
          }
        }
      } catch (e) {
        // 解析失败忽略
      }
    }

    // ==============
    // 构造转发请求
    // ==============
    const targetUrl = new URL(request.url);
    targetUrl.protocol = 'https:';
    targetUrl.hostname = 'api.telegram.org';

    const headers = new Headers(request.headers);
    headers.delete('Host');
    headers.delete(AUTH_HEADER_NAME);

    const fetchInit = {
      method: request.method,
      headers: headers,
      body: request.body,
      redirect: 'follow',
    };

    const tgResponse = await fetch(targetUrl.toString(), fetchInit);

    // ==============
    // 响应处理：如果需要删除，则记录到 KV
    // ==============
    if (monitorDeletion && tgResponse.ok && env.TG_MSG_KV) {
      const resClone = tgResponse.clone();
      try {
        const resData = await resClone.json();
        if (resData.ok && resData.result) {
          const messageId = resData.result.message_id;
          const chatId = resData.result.chat.id;
          
          // 从路径中提取 Bot Token
          const pathParts = url.pathname.split('/');
          const botTokenPart = pathParts.find(p => p.startsWith('bot'));

          if (messageId && chatId && botTokenPart) {
            const deleteTime = Date.now() + DELETE_DELAY_MS;
            // Key 格式: del_<expire_time>_<random_id>
            const key = `del_${deleteTime}_${chatId}_${messageId}`;
            
            ctx.waitUntil(
              env.TG_MSG_KV.put(key, JSON.stringify({
                chat_id: chatId,
                message_id: messageId,
                bot_token: botTokenPart,
                del_time: deleteTime
              }), {
                expiration: Math.floor(deleteTime / 1000) + 86400 
              })
            );
          }
        }
      } catch (e) {
        console.error('Error logging for deletion:', e);
      }
    }

    // 返回响应给客户端
    const responseHeaders = new Headers(tgResponse.headers);
    const cors = buildCorsHeaders();
    Object.entries(cors).forEach(([k, v]) => responseHeaders.set(k, v));

    return new Response(tgResponse.body, {
      status: tgResponse.status,
      statusText: tgResponse.statusText,
      headers: responseHeaders,
    });
  },

  /**
   * Cron Trigger 入口 (需在 wrangler.toml 配置 [triggers] crons = ["* * * * *"])
   */
  async scheduled(event, env, ctx) {
    if (!env.TG_MSG_KV) {
      console.log('KV not bound');
      return;
    }

    const now = Date.now();
    // 获取待删除任务
    const { keys } = await env.TG_MSG_KV.list({ prefix: 'del_' });

    for (const key of keys) {
      const parts = key.name.split('_');
      const expireTime = parseInt(parts[1]);

      if (expireTime <= now) {
        const value = await env.TG_MSG_KV.get(key.name, { type: 'json' });
        
        if (value) {
          const { chat_id, message_id, bot_token } = value;
          
          const deleteUrl = `${TG_API_ORIGIN}/${bot_token}/deleteMessage`;
          const deleteReq = fetch(deleteUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              chat_id: chat_id,
              message_id: message_id
            })
          });

          ctx.waitUntil(deleteReq.then(async (res) => {
             await env.TG_MSG_KV.delete(key.name);
          }));
        } else {
          ctx.waitUntil(env.TG_MSG_KV.delete(key.name));
        }
      }
    }
  }
};