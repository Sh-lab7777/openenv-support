"""
Agent Graders — score an action for a given task, ticket, and step.
Returns (reward: float, info: dict).

Reward philosophy:
  - Exact match on category/priority/dept → 1.0
  - Adjacent match → 0.5 partial credit
  - Wrong but structured → 0.1 (agent tried)
  - Missing field → 0.0

Task 3 (resolve) uses a rubric-based LLM-as-judge approach via heuristics
when an LLM is unavailable, with a clear interface for swapping in a real model.
"""

from __future__ import annotations
import re
from typing import Any

from env.models import (
    Category, Priority, Department, TaskID,
    SupportTicket, TicketAction,
)

# ── Adjacency maps for partial credit ────────────────────────────────────

# Categories that are "one step away" from each other
CATEGORY_ADJACENT: dict[Category, set[Category]] = {
    Category.BILLING:   {Category.ACCOUNT},
    Category.TECHNICAL: {Category.ACCOUNT},
    Category.ACCOUNT:   {Category.BILLING, Category.TECHNICAL},
    Category.SHIPPING:  {Category.GENERAL},
    Category.GENERAL:   {Category.SHIPPING},
}

# Priorities that are "one step away"
PRIORITY_ADJACENT: dict[Priority, set[Priority]] = {
    Priority.LOW:    {Priority.MEDIUM},
    Priority.MEDIUM: {Priority.LOW, Priority.HIGH},
    Priority.HIGH:   {Priority.MEDIUM, Priority.URGENT},
    Priority.URGENT: {Priority.HIGH},
}

# Department → canonical category mapping
DEPT_CATEGORY: dict[Department, Category] = {
    Department.BILLING_TEAM:         Category.BILLING,
    Department.TECH_SUPPORT:         Category.TECHNICAL,
    Department.ACCOUNT_MANAGEMENT:   Category.ACCOUNT,
    Department.LOGISTICS:            Category.SHIPPING,
    Department.GENERAL_SUPPORT:      Category.GENERAL,
}


# ── Main dispatcher ───────────────────────────────────────────────────────

def grade_action(
    task_id: TaskID,
    ticket: SupportTicket,
    action: TicketAction,
    step: int = 1,
) -> tuple[float, dict[str, Any]]:
    if task_id == TaskID.CLASSIFY:
        return _grade_classify(ticket, action)
    elif task_id == TaskID.PRIORITIZE:
        return _grade_prioritize(ticket, action)
    elif task_id == TaskID.RESOLVE:
        return _grade_resolve(ticket, action, step)
    else:
        raise ValueError(f"Unknown task_id: {task_id}")


# ── Task 1: Classify ──────────────────────────────────────────────────────

def _grade_classify(
    ticket: SupportTicket,
    action: TicketAction,
) -> tuple[float, dict[str, Any]]:
    gt: Category = Category(ticket.metadata["gt_category"])

    if action.category is None:
        return 0.0, {"reason": "No category provided", "gt": gt, "task_complete": True}

    if action.category == gt:
        reward = 1.0
        reason = "Exact match"
    elif action.category in CATEGORY_ADJACENT.get(gt, set()):
        reward = 0.5
        reason = "Adjacent category — partial credit"
    else:
        reward = 0.1
        reason = "Wrong category"

    return reward, {
        "reason": reason,
        "gt_category": gt,
        "predicted": action.category,
        "task_complete": True,
    }


# ── Task 2: Prioritize ────────────────────────────────────────────────────

def _grade_prioritize(
    ticket: SupportTicket,
    action: TicketAction,
) -> tuple[float, dict[str, Any]]:
    gt_priority   = Priority(ticket.metadata["gt_priority"])
    gt_department = Department(ticket.metadata["gt_department"])

    scores: dict[str, float] = {}
    reasons: dict[str, str]  = {}

    # Score priority (weight 0.5)
    if action.priority is None:
        scores["priority"] = 0.0
        reasons["priority"] = "Missing"
    elif action.priority == gt_priority:
        scores["priority"] = 1.0
        reasons["priority"] = "Exact match"
    elif action.priority in PRIORITY_ADJACENT.get(gt_priority, set()):
        scores["priority"] = 0.5
        reasons["priority"] = "Adjacent priority"
    else:
        scores["priority"] = 0.1
        reasons["priority"] = "Wrong priority"

    # Score department (weight 0.5)
    if action.assigned_department is None:
        scores["department"] = 0.0
        reasons["department"] = "Missing"
    elif action.assigned_department == gt_department:
        scores["department"] = 1.0
        reasons["department"] = "Exact match"
    else:
        # Partial credit if dept maps to right category
        dept_cat = DEPT_CATEGORY.get(action.assigned_department)
        gt_cat   = Category(ticket.metadata["gt_category"])
        if dept_cat == gt_cat:
            scores["department"] = 0.5
            reasons["department"] = "Correct category, different dept"
        else:
            scores["department"] = 0.1
            reasons["department"] = "Wrong department"

    reward = 0.5 * scores["priority"] + 0.5 * scores["department"]

    return reward, {
        "scores": scores,
        "reasons": reasons,
        "gt_priority": gt_priority,
        "gt_department": gt_department,
        "task_complete": True,
    }


# ── Task 3: Resolve ───────────────────────────────────────────────────────

RUBRIC = {
    "greeting":      (0.10, lambda draft, ticket: ticket.customer_name.split()[0].lower() in draft.lower()),
    "acknowledgement":(0.20, lambda draft, ticket: any(w in draft.lower() for w in ["apologize","sorry","understand","inconvenience","frustrat"])),
    "solution":      (0.35, lambda draft, ticket: len(draft.split()) >= 40),
    "next_step":     (0.20, lambda draft, ticket: any(w in draft.lower() for w in ["will","refund","send","investigate","escalate","contact","follow","resolve","update","within"])),
    "closing":       (0.10, lambda draft, ticket: any(w in draft.lower() for w in ["thank","sincerely","regards","best","help","feel free","reach out"])),
    "length":        (0.05, lambda draft, ticket: len(draft.split()) >= 80),
}


def _grade_resolve(
    ticket: SupportTicket,
    action: TicketAction,
    step: int,
) -> tuple[float, dict[str, Any]]:
    draft = (action.resolution_draft or "").strip()

    if not draft:
        return 0.0, {"reason": "No resolution_draft provided", "task_complete": step >= 3}

    rubric_scores: dict[str, float] = {}
    total = 0.0
    for criterion, (weight, check_fn) in RUBRIC.items():
        passed = check_fn(draft, ticket)
        rubric_scores[criterion] = weight if passed else 0.0
        total += rubric_scores[criterion]

    # Bonus: reward improvement across steps (handled externally via cumulative)
    # Small step penalty to encourage concise completion
    step_penalty = max(0, (step - 1) * 0.05)
    reward = max(0.0, round(total - step_penalty, 3))

    task_complete = reward >= 0.85 or step >= 3

    return reward, {
        "rubric_scores": rubric_scores,
        "total_before_penalty": round(total, 3),
        "step_penalty": step_penalty,
        "word_count": len(draft.split()),
        "task_complete": task_complete,
    }
