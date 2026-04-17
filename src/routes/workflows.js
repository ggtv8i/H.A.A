'use strict';

const express  = require('express');
const router   = express.Router();
const storage  = require('../storage/fileStorage');

router.get('/',     async (req, res) => {
  try { res.json(await storage.listWorkflows()); }
  catch (e) { res.status(500).json({ error: e.message }); }
});

router.get('/:id',  async (req, res) => {
  try {
    const wf = await storage.getWorkflow(req.params.id);
    if (!wf) return res.status(404).json({ error: 'Workflow not found' });
    res.json(wf);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.post('/',    async (req, res) => {
  try { res.json(await storage.saveWorkflow(req.body)); }
  catch (e) { res.status(500).json({ error: e.message }); }
});

router.put('/:id',  async (req, res) => {
  try { res.json(await storage.saveWorkflow({ ...req.body, id: req.params.id })); }
  catch (e) { res.status(500).json({ error: e.message }); }
});

router.delete('/:id', async (req, res) => {
  try { await storage.deleteWorkflow(req.params.id); res.json({ success: true }); }
  catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;
