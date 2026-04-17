'use strict';

const express  = require('express');
const router   = express.Router();
const storage  = require('../storage/fileStorage');
const { executeWorkflow } = require('../engine/executor');

/**
 * External webhook: POST /api/webhooks/:workflowId
 * Called by Telegram, GitHub, or any external service.
 */
router.all('/:workflowId', async (req, res) => {
  const wf = await storage.getWorkflow(req.params.workflowId);
  if (!wf) return res.status(404).json({ error: 'Workflow not found' });

  const hasWebhookNode = wf.nodes?.some(n =>
    ['webhook', 'telegram_trigger', 'github_event'].includes(n.type)
  );
  if (!hasWebhookNode) return res.status(400).json({ error: 'No webhook trigger in workflow' });

  const webhookData = {
    body:    req.body,
    query:   req.query,
    headers: req.headers,
    method:  req.method,
    // Telegram-specific
    message: req.body?.message?.text,
    chat_id: req.body?.message?.chat?.id,
    // GitHub-specific
    payload: req.body,
    event:   req.headers['x-github-event']
  };

  const logs = [];
  executeWorkflow({ ...wf, webhookData }, (upd) => {
    if (upd.type === 'log') logs.push(upd.message);
  }).catch(err => console.error('[Webhook exec error]', err));

  res.json({ triggered: true, workflowId: req.params.workflowId });
});

module.exports = router;
