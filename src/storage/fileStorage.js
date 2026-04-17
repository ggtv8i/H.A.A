'use strict';

const fs   = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

const DIR = path.join(__dirname, '../../workflows');

async function ensureDir() {
  await fs.mkdir(DIR, { recursive: true });
}

async function listWorkflows() {
  await ensureDir();
  const files = await fs.readdir(DIR);
  const list  = [];
  for (const f of files.filter(f => f.endsWith('.json'))) {
    try {
      const raw = await fs.readFile(path.join(DIR, f), 'utf8');
      const wf  = JSON.parse(raw);
      list.push({ id: wf.id, name: wf.name || 'Workflow', updatedAt: wf.updatedAt });
    } catch (_) {}
  }
  return list.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
}

async function getWorkflow(id) {
  await ensureDir();
  try {
    const raw = await fs.readFile(path.join(DIR, `${id}.json`), 'utf8');
    return JSON.parse(raw);
  } catch (_) { return null; }
}

async function saveWorkflow(data) {
  await ensureDir();
  const id = data.id || crypto.randomUUID();
  const wf = { ...data, id, updatedAt: new Date().toISOString() };
  await fs.writeFile(path.join(DIR, `${id}.json`), JSON.stringify(wf, null, 2));
  return wf;
}

async function deleteWorkflow(id) {
  await ensureDir();
  try { await fs.unlink(path.join(DIR, `${id}.json`)); } catch (_) {}
}

module.exports = { listWorkflows, getWorkflow, saveWorkflow, deleteWorkflow };
