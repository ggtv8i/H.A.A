'use strict';

require('dotenv').config();

const express    = require('express');
const http       = require('http');
const path       = require('path');
const cors       = require('cors');
const { WebSocketServer } = require('ws');

const workflowRoutes = require('./src/routes/workflows');
const webhookRoutes  = require('./src/routes/webhooks');
const { setupWebSocket } = require('./src/engine/executor');

// ── App ─────────────────────────────────────────────────────────
const app    = express();
const server = http.createServer(app);

// ── WebSocket ────────────────────────────────────────────────────
const wss = new WebSocketServer({ server, path: '/ws' });
setupWebSocket(wss);

// ── Middleware ──────────────────────────────────────────────────
app.use(cors());
app.use(express.json({ limit: '5mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// ── Routes ──────────────────────────────────────────────────────
app.use('/api/workflows', workflowRoutes);
app.use('/api/webhooks',  webhookRoutes);

// Health check
app.get('/api/health', (_req, res) => res.json({
  status: 'ok',
  version: '1.0.0',
  uptime: Math.round(process.uptime()),
  nodes: process.env.NODE_ENV || 'development'
}));

// Catch-all → SPA
app.get('*', (_req, res) =>
  res.sendFile(path.join(__dirname, 'public', 'index.html'))
);

// ── Start ───────────────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`\n⚡ H.A.A Flow running on http://localhost:${PORT}`);
  console.log(`   WebSocket: ws://localhost:${PORT}/ws`);
  console.log(`   Workflows API: http://localhost:${PORT}/api/workflows`);
  console.log(`\n   اضغط CTRL+C لإيقاف التشغيل\n`);
});

// Graceful shutdown
process.on('SIGTERM', () => server.close(() => process.exit(0)));
process.on('SIGINT',  () => server.close(() => process.exit(0)));
