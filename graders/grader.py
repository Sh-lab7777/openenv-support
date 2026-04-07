"""
Agent Graders — score an action for a given task, ticket, and step.
Returns (reward: float, info: dict).

All rewards are clipped to (0.01, 0.99) — strictly between 0 and 1.
"""

from __future__ import annotations
from typing import Any

from env.models import (
    Category, Priority, Department, TaskID,
    SupportTicket, TicketAction,
)

# ── Adjacency maps for partial credit ────────────────────────────────────

CATEGORY_ADJACENT: dict[Category, set[Category]] = {
    Category.BILLING:   {Category.ACCOUNT},
    Category.TECHNICAL: {Category.ACCOUNT},
    Category.ACCOUNT:   {Category.BILLING, Category.TECHNICAL},
    Category.SHIPPING:  {Category.GENERAL},
    Category.GENERAL:   {Category.SHIPPING},
}

PRIORITY_ADJACENT: dict[Priority, set[Priority]] = {
    Priority.LOW:    {Priority.MEDIUM},
    Priority.MEDIUM: {Priority.LOW, Priority.HIGH},
    Priority.HIGH:   {Priority.MEDIUM, Priority.URGENT},
    Priority.URGENT: {Priority.HIGH},
}

DEPT_CATEGORY: dict[Department, Category] = {
    Department.BILLING_TEAM:       Category.BILLING,
    Department.TECH_SUPPORT:       Category.TECHNICAL,
    Department.ACCOUNT_MANAGEMENT: Category.ACCOUNT,
    Department.LOGISTICS:          Category.SHIPPING,
    Department.GENERAL_SUPPORT:    Category.GENERAL,
}


def _clip(reward: float) -> float:
    """Clip reward to strictly (0, 1) — never 0.0 or 1.0."""
    return round(max(0.01, min(0.99, reward)), 4)


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
        return _clip(0.05), {"reason": "No category provided", "gt": gt, "task_complete": True}

    if action.category == gt:
        reward = 0.95
        reason = "Exact match"
    elif action.category in CATEGORY_ADJACENT.get(gt, set()):
        reward = 0.55
        reason = "Adjacent category — partial credit"
    else:
        reward = 0.15
        reason = "Wrong category"

    return _clip(reward), {
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

    if action.priority is None:
        scores["priority"] = 0.05
        reasons["priority"] = "Missing"
    elif action.priority == gt_priority:
        scores["priority"] = 0.95
        reasons["priority"] = "Exact match"
    elif action.priority in PRIORITY_ADJACENT.get(gt_priority, set()):
        scores["priority"] = 0.55
        reasons["priority"] = "Adjacent priority"
    else:
        scores["priority"] = 0.15
        reasons["priority"] = "Wrong priority"

    if action.assigned_department is None:
        scores["department"] = 0.05
        reasons["department"] = "Missing"
    elif action.assigned_department == gt_department:
        scores["department"] = 0.95
        reasons["department"] = "Exact match"
    else:
        dept_cat = DEPT_CATEGORY.get(action.assigned_department)
        gt_cat   = Category(ticket.metadata["gt_category"])
        if dept_cat == gt_cat:
            scores["department"] = 0.55
            reasons["department"] = "Correct category, different dept"
        else:
            scores["department"] = 0.15
            reasons["department"] = "Wrong department"

    reward = 0.5 * scores["priority"] + 0.5 * scores["department"]

    return _clip(reward), {
        "scores": scores,
        "reasons": reasons,
        "gt_priority": gt_priority,
        "gt_department": gt_department,
        "task_complete": True,
    }


# ── Task 3: Resolve ───────────────────────────────────────────────────────

RUBRIC = {
    "greeting":       (0.10, lambda d, t: t.customer_name.split()[0].lower() in d.lower()),
    "acknowledgement":(0.20, lambda d, t: any(w in d.lower() for w in ["apologize","sorry","understand","inconvenience","frustrat"])),
    "solution":       (0.30, lambda d, t: len(d.split()) >= 40),
    "next_step":      (0.20, lambda d, t: any(w in d.lower() for w in ["will","refund","send","investigate","escalate","contact","resolve","update","within"])),
    "closing":        (0.10, lambda d, t: any(w in d.lower() for w in ["thank","sincerely","regards","best","feel free","reach out"])),
    "length":         (0.05, lambda d, t: len(d.split()) >= 80),
}


def _grade_resolve(
    ticket: SupportTicket,
    action: TicketAction,
    step: int,
) -> tuple[float, dict[str, Any]]:
    draft = (action.resolution_draft or "").strip()

    if not draft:
        return _clip(0.05), {"reason": "No resolution_draft provided", "task_complete": step >= 3}

    rubric_scores: dict[str, float] = {}
    total = 0.0
    for criterion, (weight, check_fn) in RUBRIC.items():
        passed = check_fn(draft, ticket)
        rubric_scores[criterion] = weight if passed else 0.0
        total += rubric_scores[criterion]

    step_penalty = max(0, (step - 1) * 0.03)
    reward = max(0.05, round(total - step_penalty, 3))
    task_complete = reward >= 0.80 or step >= 3

    return _clip(reward), {
        "rubric_scores": rubric_scores,
        "total_before_penalty": round(total, 3),
        "step_penalty": step_penalty,
        "word_count": len(draft.split()),
        "task_complete": task_complete,
    }