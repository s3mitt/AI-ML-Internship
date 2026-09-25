/**
 * API client service for Multi-Agent Research Assistant backend.
 */

const API_BASE = '/api';

export async function fetchSystemInfo() {
  const res = await fetch(`${API_BASE}/system/info`);
  if (!res.ok) throw new Error(`Failed to fetch system info: ${res.statusText}`);
  return res.json();
}

export async function fetchWorkflowPlan() {
  const res = await fetch(`${API_BASE}/workflow-plan`);
  if (!res.ok) throw new Error(`Failed to fetch workflow plan: ${res.statusText}`);
  return res.json();
}

export async function startResearch(query, preferences = {}) {
  const res = await fetch(`${API_BASE}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, preferences }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }
  return res.json();
}

export async function fetchWorkflowById(workflowId) {
  const res = await fetch(`${API_BASE}/research/${workflowId}`);
  if (!res.ok) throw new Error(`Failed to fetch workflow: ${res.statusText}`);
  return res.json();
}

export async function listWorkflows() {
  const res = await fetch(`${API_BASE}/workflows`);
  if (!res.ok) throw new Error(`Failed to list workflows: ${res.statusText}`);
  return res.json();
}
