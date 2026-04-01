"""Typed Pydantic models for the Support Ticket OpenEnv environment."""

from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────

class Category(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    SHIPPING = "shipping"
    GENERAL = "general"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Department(str, Enum):
    BILLING_TEAM = "billing_team"
    TECH_SUPPORT = "tech_support"
    ACCOUNT_MANAGEMENT = "account_management"
    LOGISTICS = "logistics"
    GENERAL_SUPPORT = "general_support"


class TaskID(str, Enum):
    CLASSIFY = "task_classify"       # Easy  – classify ticket category
    PRIORITIZE = "task_prioritize"   # Medium – set priority + assign dept
    RESOLVE = "task_resolve"         # Hard  – draft full resolution


# ── Core domain objects ────────────────────────────────────────────────────

class SupportTicket(BaseModel):
    ticket_id: str
    subject: str
    body: str
    customer_name: str
    customer_email: str
    created_at: str                 # ISO-8601 string
    metadata: dict[str, Any] = Field(default_factory=dict)


class TicketAction(BaseModel):
    """What the agent submits for a given task."""
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    assigned_department: Optional[Department] = None
    resolution_draft: Optional[str] = None
    reasoning: Optional[str] = None  # optional chain-of-thought


# ── Observation / state ────────────────────────────────────────────────────

class Observation(BaseModel):
    ticket: SupportTicket
    task_id: TaskID
    task_description: str
    step_number: int
    max_steps: int
    instructions: str


class StepResult(BaseModel):
    observation: Observation
    reward: float = Field(ge=0.0, le=1.0)
    done: bool
    info: dict[str, Any] = Field(default_factory=dict)


class EnvironmentState(BaseModel):
    episode_id: str
    task_id: TaskID
    current_step: int
    max_steps: int
    ticket: SupportTicket
    last_action: Optional[TicketAction] = None
    cumulative_reward: float = 0.0
    done: bool = False
