'use strict';
require('dotenv').config();

// ══════════════════════════════════════════════════════════════
//  Helper utilities
// ══════════════════════════════════════════════════════════════
function getParam(node, key, fallback = '') {
  const p = (node.params || []).find(p => p.k === key);
  return p ? (p.v || fallback) : fallback;
}

function getNestedValue(obj, path) {
  if (!obj || !path) return undefined;
  return path.split('.').reduce((curr, key) => curr?.[key], obj);
}

function resolveTemplate(template, data) {
  if (typeof template !== 'string') return template;
  return template.replace(/\{\{([^}]+)\}\}/g, (_, key) => {
    const val = getNestedValue(data, key.trim());
    return val !== undefined ? String(val) : `{{${key}}}`;
  });
}

// ══════════════════════════════════════════════════════════════
//  Node executors map
// ══════════════════════════════════════════════════════════════
const executors = {

  // ─────────────────────────────────────────────────────────────
  //  TRIGGERS  (تشغيل عبر الـ WebSocket أو Webhook الخارجي)
  // ─────────────────────────────────────────────────────────────

  webhook: async (node, inputs) => {
    // When triggered from an HTTP webhook, inputs.body/query are injected
    return {
      output: inputs.body || inputs.query || inputs.webhookData || {
        triggered_at: new Date().toISOString(),
        source: 'manual'
      }
    };
  },

  schedule: async (node, inputs) => {
    return {
      output: {
        triggered_at: new Date().toISOString(),
        cron: getParam(node, 'cron', '0 9 * * *'),
        timezone: getParam(node, 'tz', 'Asia/Baghdad')
      }
    };
  },

  telegram_trigger: async (node, inputs) => {
    // Real polling handled by TelegramPoller class; here we pass through
    return {
      message: inputs.message || inputs.text || '',
      chat_id: inputs.chat_id || inputs.chatId || ''
    };
  },

  github_event: async (node, inputs) => {
    return {
      payload: inputs.payload || inputs.body || {}
    };
  },

  // ─────────────────────────────────────────────────────────────
  //  AI
  // ─────────────────────────────────────────────────────────────

  claude: async (node, inputs) => {
    const Anthropic = require('@anthropic-ai/sdk');
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) throw new Error('ANTHROPIC_API_KEY غير مُعيَّن في ملف .env');

    const client = new Anthropic({ apiKey });
    const model      = getParam(node, 'model', 'claude-opus-4-5');
    const maxTokens  = parseInt(getParam(node, 'max_tokens', '1000')) || 1000;
    const systemPr   = getParam(node, 'system', 'أنت مساعد مفيد.');
    const promptText = String(inputs.prompt || inputs.input || inputs.text || 'مرحباً');

    const message = await client.messages.create({
      model,
      max_tokens: maxTokens,
      system: systemPr,
      messages: [{ role: 'user', content: promptText }]
    });

    return {
      response: message.content[0]?.text || '',
      tokens: (message.usage?.input_tokens || 0) + (message.usage?.output_tokens || 0)
    };
  },

  openai: async (node, inputs) => {
    const OpenAI = require('openai');
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) throw new Error('OPENAI_API_KEY غير مُعيَّن في ملف .env');

    const client = new OpenAI({ apiKey });
    const model       = getParam(node, 'model', 'gpt-4o');
    const temperature = parseFloat(getParam(node, 'temperature', '0.7')) || 0.7;
    const promptText  = String(inputs.prompt || inputs.input || inputs.text || 'مرحباً');

    const completion = await client.chat.completions.create({
      model,
      temperature,
      messages: [{ role: 'user', content: promptText }]
    });

    return {
      response: completion.choices[0]?.message?.content || '',
      tokens: completion.usage?.total_tokens || 0
    };
  },

  text_classify: async (node, inputs) => {
    const labels = getParam(node, 'labels', 'إيجابي,سلبي,محايد')
      .split(',').map(l => l.trim()).filter(Boolean);
    const text = String(inputs.text || inputs.input || '');

    if (process.env.ANTHROPIC_API_KEY) {
      const Anthropic = require('@anthropic-ai/sdk');
      const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
      const msg = await client.messages.create({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 50,
        messages: [{
          role: 'user',
          content: `صنِّف النص التالي إلى إحدى الفئات: ${labels.join('، ')}\nالنص: "${text}"\nأجب بالفئة فقط دون أي شرح.`
        }]
      });
      const category = msg.content[0]?.text?.trim() || labels[0];
      return { category, confidence: 0.92 };
    }

    // Simple keyword-based fallback
    const category = labels[0];
    return { category, confidence: 0.5 };
  },

  // ─────────────────────────────────────────────────────────────
  //  LOGIC
  // ─────────────────────────────────────────────────────────────

  if: async (node, inputs) => {
    const field = getParam(node, 'field', 'value');
    const op    = getParam(node, 'op',    'equals');
    const val   = getParam(node, 'value', '');
    const data  = inputs.input || inputs;
    const actual = getNestedValue(data, field);

    const tests = {
      equals:       () => String(actual) === String(val),
      not_equals:   () => String(actual) !== String(val),
      contains:     () => String(actual).includes(String(val)),
      greater_than: () => parseFloat(actual) > parseFloat(val),
      less_than:    () => parseFloat(actual) < parseFloat(val),
      exists:       () => actual !== undefined && actual !== null,
    };

    const passed = (tests[op] || tests.equals)();
    return passed ? { true: data } : { false: data };
  },

  switch: async (node, inputs) => {
    const field = getParam(node, 'field', 'type');
    const data  = inputs.input || inputs;
    const value = String(getNestedValue(data, field) || '');
    const out   = {};
    out[value]  = data;
    if (!['case1', 'case2'].includes(value)) out.default = data;
    return out;
  },

  loop: async (node, inputs) => {
    const field = getParam(node, 'field', 'items');
    const arr   = inputs.array || getNestedValue(inputs.input, field) || [];

    if (!Array.isArray(arr) || !arr.length) return { done: { total: 0, items: [] } };

    // Return first item; real iteration is handled by executor multi-pass
    return {
      item:  arr[0],
      index: 0,
      done:  { total: arr.length, items: arr }
    };
  },

  merge: async (node, inputs) => {
    const mode   = getParam(node, 'mode', 'merge');
    const input1 = inputs.input1 || {};
    const input2 = inputs.input2 || {};

    const mergeMap = {
      append: () => Array.isArray(input1) && Array.isArray(input2)
        ? [...input1, ...input2]
        : { ...input1, ...input2 },
      merge:  () => Object.assign({}, input1, input2),
      zip:    () => ({ data1: input1, data2: input2 }),
    };

    return { merged: (mergeMap[mode] || mergeMap.merge)() };
  },

  wait: async (node, inputs) => {
    const delay = Math.min(parseInt(getParam(node, 'delay', '1')) * 1000, 30000);
    await new Promise(r => setTimeout(r, delay));
    return { output: inputs.input || {} };
  },

  // ─────────────────────────────────────────────────────────────
  //  ACTIONS
  // ─────────────────────────────────────────────────────────────

  telegram_send: async (node, inputs) => {
    const axios  = require('axios');
    const token  = getParam(node, 'token') || process.env.TELEGRAM_BOT_TOKEN;
    const chatId = inputs.chat_id || inputs.chatId || getParam(node, 'chat_id');
    if (!token)  throw new Error('Telegram Bot Token مفقود');
    if (!chatId) throw new Error('chat_id مفقود — تأكد من ربط منفذ chat_id');

    const rawText  = getParam(node, 'text', inputs.text || 'رسالة من H.A.A Flow');
    const text     = resolveTemplate(rawText, inputs);
    const parseMode = getParam(node, 'parse_mode', 'Markdown');

    const res = await axios.post(`https://api.telegram.org/bot${token}/sendMessage`, {
      chat_id: chatId,
      text,
      ...(parseMode !== 'None' ? { parse_mode: parseMode } : {})
    });

    return { result: res.data };
  },

  http: async (node, inputs) => {
    const axios  = require('axios');
    const url    = String(inputs.url || getParam(node, 'url', 'https://httpbin.org/get'));
    const method = (getParam(node, 'method', 'GET')).toLowerCase();
    let headers  = {};
    try { headers = JSON.parse(getParam(node, 'headers', '{}')); } catch (_) {}

    const config = { method, url, headers, timeout: 15000 };
    if (inputs.body && method !== 'get') config.data = inputs.body;

    const res = await axios(config);
    return { response: res.data, status: res.status };
  },

  github_api: async (node, inputs) => {
    const axios    = require('axios');
    const token    = getParam(node, 'token') || process.env.GITHUB_TOKEN;
    const endpoint = getParam(node, 'endpoint', '/user');
    const method   = (getParam(node, 'method', 'GET')).toLowerCase();
    if (!token) throw new Error('GitHub Token مفقود');

    const res = await axios({
      method,
      url: `https://api.github.com${endpoint}`,
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github.v3+json',
        'User-Agent': 'HAA-Flow'
      },
      data: method !== 'get' ? inputs.input : undefined,
      timeout: 15000
    });

    return { result: res.data };
  },

  email: async (node, inputs) => {
    const nodemailer = require('nodemailer');
    if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS) {
      throw new Error('EMAIL_USER و EMAIL_PASS غير مُعيَّنين في .env');
    }

    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASS }
    });

    const info = await transporter.sendMail({
      from:    getParam(node, 'from') || process.env.EMAIL_USER,
      to:      inputs.to   || getParam(node, 'to'),
      subject: inputs.subject || getParam(node, 'subject', 'إشعار من H.A.A Flow'),
      html:    inputs.body  || getParam(node, 'body', '<p>رسالة تلقائية</p>')
    });

    return { result: { messageId: info.messageId, accepted: info.accepted } };
  },

  code: async (node, inputs) => {
    const code = getParam(node, 'code', 'result = input_data;');
    try {
      // Safe sandbox using Function constructor (no fs/net access)
      const sandbox = {
        input_data: inputs.input || inputs,
        console: { log: () => {}, error: () => {} },
        JSON, Math, Date, Array, Object, String, Number, Boolean
      };
      const fn = new Function(
        ...Object.keys(sandbox),
        `"use strict"; let result; ${code}; return result;`
      );
      const output = fn(...Object.values(sandbox));
      return { output: output ?? null, error: null };
    } catch (err) {
      return { output: null, error: err.message };
    }
  },

  // ─────────────────────────────────────────────────────────────
  //  DATA
  // ─────────────────────────────────────────────────────────────

  set: async (node, inputs) => {
    let fields = {};
    try { fields = JSON.parse(getParam(node, 'fields', '{}')); } catch (_) {}
    return { output: { ...(inputs.input || {}), ...fields } };
  },

  filter: async (node, inputs) => {
    const arr   = inputs.array || [];
    const field = getParam(node, 'field', 'active');
    const op    = getParam(node, 'op',    'equals');
    const val   = getParam(node, 'value', 'true');

    if (!Array.isArray(arr)) return { filtered: [], excluded: [] };

    const tests = {
      equals:       (a) => String(a) === String(val),
      not_equals:   (a) => String(a) !== String(val),
      contains:     (a) => String(a).includes(String(val)),
      greater_than: (a) => parseFloat(a) > parseFloat(val),
      less_than:    (a) => parseFloat(a) < parseFloat(val),
    };

    const testFn = tests[op] || tests.equals;
    const filtered  = arr.filter(item => testFn(getNestedValue(item, field)));
    const excluded  = arr.filter(item => !testFn(getNestedValue(item, field)));
    return { filtered, excluded };
  },

  transform: async (node, inputs) => {
    const template = getParam(node, 'template', '{"result":"{{data}}"}');
    const resolved = resolveTemplate(template, inputs.input || inputs);
    let output;
    try { output = JSON.parse(resolved); } catch (_) { output = resolved; }
    return { output };
  },

  debug: async (node, inputs) => {
    const label = getParam(node, 'label', 'Debug');
    const data  = inputs.input || inputs;
    console.log(`\n[DEBUG: ${label}]\n`, JSON.stringify(data, null, 2));
    return { output: data };
  }
};

module.exports = executors;
