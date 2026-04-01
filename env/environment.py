"""
Support Ticket Resolution — OpenEnv Environment
Implements the standard step() / reset() / state() API.
"""

from __future__ import annotations
import uuid
import random
from datetime import datetime, timezone
from typing import Any

from env.models import (
    Category, Priority, Department, TaskID,
    SupportTicket, TicketAction, Observation, StepResult, EnvironmentState,
)
from env.ticket_bank import TICKET_BANK
from graders.grader import grade_action


# ── Task metadata ──────────────────────────────────────────────────────────

TASK_META = {
    TaskID.CLASSIFY: {
        "description": "Classify the support ticket into the correct category.",
        "instructions": (
            "Read the ticket carefully. Set `category` to one of: "
            "billing, technical, account, shipping, general. "
            "Optionally provide `reasoning`."
        ),
        "max_steps": 1,
    },
    TaskID.PRIORITIZE: {
        "description": "Assign a priority level and route the ticket to the right department.",
        "instructions": (
            "Assess urgency and set `priority` (low/medium/high/urgent) "
            "and `assigned_department` (billing_team/tech_support/"
            "account_management/logistics/general_support). "
            "Optionally provide `reasoning`."
        ),
        "max_steps": 1,
    },
    TaskID.RESOLVE: {
        "description": "Draft a complete, empathetic resolution reply to the customer.",
        "instructions": (
            "Write a professional reply in `resolution_draft`. "
            "It must: greet the customer by name, acknowledge the issue, "
            "provide a concrete solution or next step, and close politely. "
            "Minimum 80 words."
        ),
        "max_steps": 3,   # agent may refine across up to 3 steps
    },
}


class SupportTicketEnv:
    """
    OpenEnv-compatible environment for customer support ticket resolution.

    Tasks (increasing difficulty):
      task_classify   – Easy   – classify ticket category
      task_prioritize – Medium – set priority + assign department
      task_resolve    – Hard   – draft a full customer-facing resolution
    """

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def reset(
        self,
        task_id: TaskID | str = TaskID.CLASSIFY,
        ticket: SupportTicket | None = None,
        seed: int | None = None,
    ) -> Observation:
        """Start a new episode. Returns the first observation."""
        if seed is not None:
            random.seed(seed)

        if isinstance(task_id, str):
            task_id = TaskID(task_id)

        ticket = ticket or random.choice(TICKET_BANK)
        meta = TASK_META[task_id]

        self._state = EnvironmentState(
            episode_id=str(uuid.uuid4())[:8],
            task_id=task_id,
            current_step=0,
            max_steps=meta["max_steps"],
            ticket=ticket,
            done=False,
            cumulative_reward=0.0,
        )
        return self._make_obs()

    def step(self, action: TicketAction | dict[str, Any]) -> StepResult:
        """
        Submit an action. Returns (observation, reward, done, info).

        reward — float in [0, 1] representing quality of this action
        done   — True when the episode is complete
        """
        if not hasattr(self, "_state"):
            raise RuntimeError("Call reset() before step().")
        if self._state.done:
            raise RuntimeError("Episode is done. Call reset() to start a new one.")

        if isinstance(action, dict):
            action = TicketAction(**action)

        self._state.current_step += 1
        self._state.last_action = action

        reward, info = grade_action(
            task_id=self._state.task_id,
            ticket=self._state.ticket,
            action=action,
            step=self._state.current_step,
        )
        self._state.cumulative_reward += reward

        done = (
            self._state.current_step >= self._state.max_steps
            or info.get("task_complete", False)
        )
        self._state.done = done

        obs = self._make_obs()
        return StepResult(observation=obs, reward=reward, done=done, info=info)

    def state(self) -> EnvironmentState:
        """Return a full snapshot of the current environment state."""
        if not hasattr(self, "_state"):
            raise RuntimeError("Call reset() first.")
        return self._state.model_copy()

    # ── Internal helpers ───────────────────────────────────────────────────

    def _make_obs(self) -> Observation:
        meta = TASK_META[self._state.task_id]
        return Observation(
            ticket=self._state.ticket,
            task_id=self._state.task_id,
            task_description=meta["description"],
            step_number=self._state.current_step,
            max_steps=self._state.max_steps,
            instructions=meta["instructions"],
        )

    # ── Convenience ────────────────────────────────────────────────────────

    @property
    def observation_space(self) -> dict:
        return {
            "ticket": "SupportTicket — id, subject, body, customer info",
            "task_id": "TaskID enum — classify | prioritize | resolve",
            "task_description": "str — human-readable task goal",
            "step_number": "int",
            "max_steps": "int",
            "instructions": "str — action format guidance",
        }

    @property
    def action_space(self) -> dict:
        return {
            "category": "Category? — billing|technical|account|shipping|general",
            "priority": "Priority? — low|medium|high|urgent",
            "assigned_department": "Department? — billing_team|tech_support|...",
            "resolution_draft": "str? — customer-facing reply (task_resolve only)",
            "reasoning": "str? — optional chain-of-thought",
        }
