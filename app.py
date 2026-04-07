"""
FastAPI application — exposes SupportTicketEnv over HTTP.
Deployed to Hugging Face Spaces via Dockerfile.

Endpoints:
  GET  /         — Beautiful dashboard UI
  POST /reset    — start episode
  POST /step     — submit action
  GET  /state    — get current state
  GET  /tasks    — list available tasks
  GET  /health   — liveness probe
"""

from __future__ import annotations
import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import sys
sys.path.insert(0, ".")

from env.environment import SupportTicketEnv
from env.models import (
    TaskID, TicketAction, StepResult, EnvironmentState, Observation,
    Category, Priority, Department,
)

app = FastAPI(
    title="SupportTicketEnv — OpenEnv",
    description="Customer Support Ticket Resolution environment for AI agent training.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_env = SupportTicketEnv()

DASHBOARD_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SupportTicketEnv — OpenEnv</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0a0a0f; color: #e8e6f0; font-family: 'DM Mono', monospace; min-height: 100vh; overflow-x: hidden; }
  .grid-bg {
    position: fixed; inset: 0; z-index: 0;
    background-image: linear-gradient(rgba(99,102,241,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.06) 1px, transparent 1px);
    background-size: 40px 40px;
  }
  .container { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; padding: 48px 24px; }
  .badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc; padding: 6px 14px; border-radius: 100px;
    font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 24px; animation: fadeUp 0.5s ease both;
  }
  .dot { width: 6px; height: 6px; background: #22c55e; border-radius: 50%; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
  h1 { font-family: 'Syne', sans-serif; font-size: clamp(32px, 6vw, 52px); font-weight: 800; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 16px; animation: fadeUp 0.5s 0.1s ease both; }
  h1 span { color: #818cf8; }
  .subtitle { color: #6b7280; font-size: 14px; line-height: 1.7; margin-bottom: 48px; animation: fadeUp 0.5s 0.2s ease both; }
  .tasks-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 48px; }
  .task-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 24px; transition: all 0.2s ease; animation: fadeUp 0.5s ease both; cursor: pointer;
  }
  .task-card:hover { background: rgba(255,255,255,0.06); border-color: rgba(99,102,241,0.4); transform: translateY(-2px); }
  .task-card:nth-child(1) { animation-delay: 0.3s; }
  .task-card:nth-child(2) { animation-delay: 0.4s; }
  .task-card:nth-child(3) { animation-delay: 0.5s; }
  .task-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
  .task-id { font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: #4b5563; }
  .difficulty { font-size: 10px; padding: 3px 10px; border-radius: 100px; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500; }
  .easy   { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
  .medium { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
  .hard   { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
  .task-name { font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; margin-bottom: 8px; }
  .task-desc { font-size: 12px; color: #6b7280; line-height: 1.6; margin-bottom: 16px; }
  .score-bar { height: 3px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; }
  .score-fill { height: 100%; border-radius: 2px; background: linear-gradient(90deg, #6366f1, #a855f7); width: 0; transition: width 1s ease; }
  .score-label { font-size: 10px; color: #4b5563; margin-top: 6px; }
  .endpoints { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 28px; animation: fadeUp 0.5s 0.6s ease both; margin-bottom: 32px; }
  .endpoints h2 { font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700; margin-bottom: 20px; color: #9ca3af; }
  .endpoint { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
  .endpoint:last-child { border-bottom: none; }
  .method { font-size: 10px; font-weight: 500; padding: 3px 8px; border-radius: 4px; min-width: 40px; text-align: center; }
  .get  { background: rgba(34,197,94,0.15);  color: #4ade80; }
  .post { background: rgba(99,102,241,0.15); color: #a5b4fc; }
  .path { font-size: 13px; color: #e8e6f0; flex: 1; }
  .desc-e { font-size: 11px; color: #4b5563; }
  .footer { display: flex; gap: 12px; flex-wrap: wrap; animation: fadeUp 0.5s 0.7s ease both; }
  .btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: 10px; font-size: 12px; font-family: 'DM Mono', monospace; cursor: pointer; text-decoration: none; transition: all 0.2s; letter-spacing: 0.05em; }
  .btn-primary { background: #6366f1; color: white; border: none; }
  .btn-primary:hover { background: #4f46e5; transform: translateY(-1px); }
  .btn-outline { background: transparent; color: #9ca3af; border: 1px solid rgba(255,255,255,0.1); }
  .btn-outline:hover { border-color: rgba(99,102,241,0.4); color: #e8e6f0; }
  @keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
</style>
</head>
<body>
<div class="grid-bg"></div>
<div class="container">
  <div class="badge"><div class="dot"></div>Live · OpenEnv v1.0.0</div>
  <h1>Support<span>Ticket</span><br>Env</h1>
  <p class="subtitle">A real-world OpenEnv environment for AI agent training.<br>Classify, prioritise, and resolve customer support tickets.</p>
  <div class="tasks-grid">
    <div class="task-card" onclick="window.location='/docs'">
      <div class="task-header"><span class="task-id">task_classify</span><span class="difficulty easy">Easy</span></div>
      <div class="task-name">Classify</div>
      <div class="task-desc">Identify the correct category for an incoming support ticket.</div>
      <div class="score-bar"><div class="score-fill" data-width="80"></div></div>
      <div class="score-label">Baseline score: 0.795</div>
    </div>
    <div class="task-card" onclick="window.location='/docs'">
      <div class="task-header"><span class="task-id">task_prioritize</span><span class="difficulty medium">Medium</span></div>
      <div class="task-name">Prioritise</div>
      <div class="task-desc">Assign urgency level and route to the correct department.</div>
      <div class="score-bar"><div class="score-fill" data-width="76"></div></div>
      <div class="score-label">Baseline score: 0.763</div>
    </div>
    <div class="task-card" onclick="window.location='/docs'">
      <div class="task-header"><span class="task-id">task_resolve</span><span class="difficulty hard">Hard</span></div>
      <div class="task-name">Resolve</div>
      <div class="task-desc">Draft a complete, empathetic customer-facing resolution reply.</div>
      <div class="score-bar"><div class="score-fill" data-width="100"></div></div>
      <div class="score-label">Baseline score: 1.000</div>
    </div>
  </div>
  <div class="endpoints">
    <h2>API Endpoints</h2>
    <div class="endpoint"><span class="method post">POST</span><span class="path">/reset</span><span class="desc-e">Start a new episode</span></div>
    <div class="endpoint"><span class="method post">POST</span><span class="path">/step</span><span class="desc-e">Submit an action → reward</span></div>
    <div class="endpoint"><span class="method get">GET</span><span class="path">/state</span><span class="desc-e">Full environment snapshot</span></div>
    <div class="endpoint"><span class="method get">GET</span><span class="path">/tasks</span><span class="desc-e">List all tasks</span></div>
    <div class="endpoint"><span class="method get">GET</span><span class="path">/health</span><span class="desc-e">Liveness probe</span></div>
  </div>
  <div class="footer">
    <a class="btn btn-primary" href="/docs">Interactive Docs →</a>
    <a class="btn btn-outline" href="/tasks">JSON API</a>
    <a class="btn btn-outline" href="/health">Health Check</a>
  </div>
</div>
<script>
  setTimeout(() => { document.querySelectorAll('.score-fill').forEach(el => { el.style.width = el.dataset.width + '%'; }); }, 600);
</script>
</body>
</html>"""


# ── Request schemas ────────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_id: Optional[str] = "task_classify"
    seed: Optional[int] = None
    class Config:
        extra = "allow"


class StepRequest(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = None
    assigned_department: Optional[str] = None
    resolution_draft: Optional[str] = None
    reasoning: Optional[str] = None
    class Config:
        extra = "allow"


# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def root():
    return DASHBOARD_HTML


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {"id": "task_classify",   "difficulty": "easy",   "description": "Classify the ticket into the correct category.",         "score_range": [0.0, 1.0]},
            {"id": "task_prioritize", "difficulty": "medium", "description": "Assign priority and route to the right department.",      "score_range": [0.0, 1.0]},
            {"id": "task_resolve",    "difficulty": "hard",   "description": "Draft a complete, empathetic customer resolution reply.", "score_range": [0.0, 1.0]},
        ],
        "observation_space": _env.observation_space,
        "action_space": _env.action_space,
    }


@app.post("/reset", response_model=dict)
async def reset(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    task_id_str = body.get("task_id", "task_classify") or "task_classify"
    seed = body.get("seed", None)
    try:
        task_id = TaskID(task_id_str)
    except ValueError:
        raise HTTPException(400, f"Unknown task_id '{task_id_str}'. Valid: {[t.value for t in TaskID]}")
    obs = _env.reset(task_id=task_id, seed=seed)
    return obs.model_dump()


@app.post("/step", response_model=dict)
async def step(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    try:
        action = TicketAction(
            category=Category(body["category"]) if body.get("category") else None,
            priority=Priority(body["priority"]) if body.get("priority") else None,
            assigned_department=Department(body["assigned_department"]) if body.get("assigned_department") else None,
            resolution_draft=body.get("resolution_draft"),
            reasoning=body.get("reasoning"),
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    try:
        result = _env.step(action)
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    return result.model_dump()


@app.get("/state", response_model=dict)
def get_state():
    try:
        s = _env.state()
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    return s.model_dump()


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()