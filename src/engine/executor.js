'use strict';

const nodeExecutors = require('./nodeExecutors');

// ══════════════════════════════════════════════════════════════
//  WebSocket manager
// ══════════════════════════════════════════════════════════════
const clients = new Map();

function setupWebSocket(wss) {
  wss.on('connection', (ws) => {
    const id = Math.random().toString(36).slice(2, 10);
    ws.clientId = id;
    clients.set(id, ws);

    ws.send(JSON.stringify({ type: 'connected', clientId: id }));

    ws.on('message', async (raw) => {
      let msg;
      try { msg = JSON.parse(raw); } catch (_) { return; }

      if (msg.type === 'execute') {
        try {
          await executeWorkflow(msg.workflow, (update) => safeSend(ws, update));
        } catch (err) {
          safeSend(ws, { type: 'error', message: err.message });
        }
      }
    });

    ws.on('close', () => clients.delete(id));
    ws.on('error', () => clients.delete(id));
  });
}

function safeSend(ws, data) {
  try {
    if (ws.readyState === 1) ws.send(JSON.stringify(data));
  } catch (_) {}
}

// Broadcast to a specific client
function broadcast(clientId, data) {
  const ws = clients.get(clientId);
  if (ws) safeSend(ws, data);
}

// ══════════════════════════════════════════════════════════════
//  Topological sort
// ══════════════════════════════════════════════════════════════
function topologicalSort(nodes, connections) {
  const visited = new Set();
  const result  = [];
  const adj     = Object.fromEntries(nodes.map(n => [n.id, []]));

  connections.forEach(c => {
    if (adj[c.from]) adj[c.from].push(c.to);
  });

  function visit(id) {
    if (visited.has(id)) return;
    visited.add(id);
    (adj[id] || []).forEach(visit);
    const node = nodes.find(n => n.id === id);
    if (node) result.unshift(node);
  }

  nodes.forEach(n => visit(n.id));
  return result;
}

// ══════════════════════════════════════════════════════════════
//  Main execution engine
// ══════════════════════════════════════════════════════════════
async function executeWorkflow(workflow, sendUpdate) {
  const { nodes = [], connections = [] } = workflow;

  if (!nodes.length) {
    sendUpdate({ type: 'log', level: 'warn', message: 'لا توجد نودات في الـ Workflow!' });
    return;
  }

  const log  = (level, message) => sendUpdate({ type: 'log', level, message });
  const status = (nodeId, s, extra = {}) =>
    sendUpdate({ type: 'node_status', nodeId, status: s, ...extra });

  log('run', '════ بدء تنفيذ الـ Workflow ════');
  nodes.forEach(n => status(n.id, 'idle'));

  const order = topologicalSort(nodes, connections);
  log('info', `ترتيب التنفيذ: ${order.map(n => n.label).join(' → ')}`);

  const nodeOutputs = {};

  for (const node of order) {
    status(node.id, 'running');
    log('run', `▶ ${node.icon || '●'} ${node.label} (${node.type})`);

    // ── Collect inputs from upstream connections ──────────────
    const inputs = {};
    connections
      .filter(c => c.to === node.id)
      .forEach(c => {
        const fromOut = nodeOutputs[c.from];
        if (fromOut !== undefined) {
          // If fromOut has a key matching the fromPort, use it; else use entire output
          inputs[c.toPort] = (fromOut[c.fromPort] !== undefined)
            ? fromOut[c.fromPort]
            : fromOut;
        }
      });

    // Inject webhook/trigger data on trigger nodes
    if (workflow.webhookData && !connections.some(c => c.to === node.id)) {
      Object.assign(inputs, workflow.webhookData);
    }

    // ── Execute ───────────────────────────────────────────────
    try {
      const executor = nodeExecutors[node.type];
      if (!executor) throw new Error(`نوع النود غير مدعوم: ${node.type}`);

      const output = await executor(node, inputs);
      nodeOutputs[node.id] = output;

      // Activate outgoing connections
      connections
        .filter(c => c.from === node.id)
        .forEach(c => sendUpdate({ type: 'activate_connection', connId: c.id }));

      const preview = JSON.stringify(output).slice(0, 200);
      status(node.id, 'done', { preview });
      log('ok', `✓ ${node.label} → ${preview}`);

    } catch (err) {
      status(node.id, 'error');
      log('err', `✗ فشل ${node.label}: ${err.message}`);
      // Continue with next node (non-fatal by default)
    }
  }

  log('ok', '════ انتهى التنفيذ ════');
  sendUpdate({ type: 'execution_complete' });
}

module.exports = { setupWebSocket, executeWorkflow, broadcast };
