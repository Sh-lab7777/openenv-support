"""
FastAPI application — exposes SupportTicketEnv over HTTP.
Deployed to Hugging Face Spaces via Dockerfile.

Endpoints:
  POST /reset     — start episode
  POST /step      — submit action
  GET  /state     — get current state
  GET  /tasks     — list available tasks
  GET  /health    — liveness probe
"""

from __future__ import annotations
import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
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

# One env per process (stateless via reset)
_env = SupportTicketEnv()


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

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "id": "task_classify",
                "difficulty": "easy",
                "description": "Classify the ticket into the correct category.",
                "score_range": [0.0, 1.0],
            },
            {
                "id": "task_prioritize",
                "difficulty": "medium",
                "description": "Assign priority and route to the right department.",
                "score_range": [0.0, 1.0],
            },
            {
                "id": "task_resolve",
                "difficulty": "hard",
                "description": "Draft a complete, empathetic customer resolution reply.",
                "score_range": [0.0, 1.0],
            },
        ],
        "observation_space": _env.observation_space,
        "action_space": _env.action_space,
    }


@app.post("/reset", response_model=dict)
async def reset(request: Request):
    # Accept empty body or JSON body
    try:
        body = await request.json()
    except Exception:
        body = {}

    task_id_str = body.get("task_id", "task_classify") or "task_classify"
    seed = body.get("seed", None)

    try:
        task_id = TaskID(task_id_str)
    except ValueError:
        raise HTTPException(400, f"Unknown task_id '{task_id_str}'. "
                                 f"Valid: {[t.value for t in TaskID]}")
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