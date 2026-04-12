"""
Agent Graders — LLM-as-Judge for Task 3, heuristic fallback.
All rewards strictly between 0 and 1 via _clip().
"""

from __future__ import annotations
import json
import os
from typing import Any

from env.models import (
    Category, Priority, Department, TaskID,
    SupportTicket, TicketAction,
)


def _clip(r: float) -> float:
    return round(max(0.01, min(0.99, r)), 4)


CATEGORY_ADJACENT = {
    Category.BILLING:   {Category.ACCOUNT},
    Category.TECHNICAL: {Category.ACCOUNT},
    Category.ACCOUNT:   {Category.BILLING, Category.TECHNICAL},
    Category.SHIPPING:  {Category.GENERAL},
    Category.GENERAL:   {Category.SHIPPING},
}

PRIORITY_ADJACENT = {
    Priority.LOW:    {Priority.MEDIUM},
    Priority.MEDIUM: {Priority.LOW, Priority.HIGH},
    Priority.HIGH:   {Priority.MEDIUM, Priority.URGENT},
    Priority.URGENT: {Priority.HIGH},
}

DEPT_CATEGORY = {
    Department.BILLING_TEAM:       Category.BILLING,
    Department.TECH_SUPPORT:       Category.TECHNICAL,
    Department.ACCOUNT_MANAGEMENT: Category.ACCOUNT,
    Department.LOGISTICS:          Category.SHIPPING,
    Department.GENERAL_SUPPORT:    Category.GENERAL,
}


def grade_action(task_id, ticket, action, step=1):
    if task_id == TaskID.CLASSIFY:
        return _grade_classify(ticket, action)
    elif task_id == TaskID.PRIORITIZE:
        return _grade_prioritize(ticket, action)
    elif task_id == TaskID.RESOLVE:
        return _grade_resolve(ticket, action, step)
    raise ValueError(f"Unknown task_id: {task_id}")


def _grade_classify(ticket, action):
    gt = Category(ticket.metadata["gt_category"])
    if action.category is None:
        return _clip(0.05), {"reason": "No category", "gt": gt, "task_complete": True}
    if action.category == gt:
        r, reason = 0.95, "Exact match"
    elif action.category in CATEGORY_ADJACENT.get(gt, set()):
        r, reason = 0.55, "Adjacent category"
    else:
        r, reason = 0.15, "Wrong category"
    return _clip(r), {"reason": reason, "gt_category": gt, "predicted": action.category, "task_complete": True}


def _grade_prioritize(ticket, action):
    gt_p = Priority(ticket.metadata["gt_priority"])
    gt_d = Department(ticket.metadata["gt_department"])
    scores, reasons = {}, {}

    if action.priority is None:
        scores["priority"], reasons["priority"] = 0.05, "Missing"
    elif action.priority == gt_p:
        scores["priority"], reasons["priority"] = 0.95, "Exact"
    elif action.priority in PRIORITY_ADJACENT.get(gt_p, set()):
        scores["priority"], reasons["priority"] = 0.55, "Adjacent"
    else:
        scores["priority"], reasons["priority"] = 0.15, "Wrong"

    if action.assigned_department is None:
        scores["department"], reasons["department"] = 0.05, "Missing"
    elif action.assigned_department == gt_d:
        scores["department"], reasons["department"] = 0.95, "Exact"
    else:
        dc = DEPT_CATEGORY.get(action.assigned_department)
        gc = Category(ticket.metadata["gt_category"])
        if dc == gc:
            scores["department"], reasons["department"] = 0.55, "Right category"
        else:
            scores["department"], reasons["department"] = 0.15, "Wrong"

    r = 0.5 * scores["priority"] + 0.5 * scores["department"]
    return _clip(r), {"scores": scores, "reasons": reasons, "gt_priority": gt_p, "gt_department": gt_d, "task_complete": True}


RUBRIC = {
    "greeting":       (0.10, lambda d, t: t.customer_name.split()[0].lower() in d.lower()),
    "acknowledgement":(0.20, lambda d, t: any(w in d.lower() for w in ["apologize","sorry","understand","inconvenience","frustrat"])),
    "solution":       (0.30, lambda d, t: len(d.split()) >= 40),
    "next_step":      (0.20, lambda d, t: any(w in d.lower() for w in ["will","refund","send","investigate","escalate","resolve","update","within"])),
    "closing":        (0.10, lambda d, t: any(w in d.lower() for w in ["thank","sincerely","regards","best","feel free","reach out"])),
    "length":         (0.05, lambda d, t: len(d.split()) >= 80),
}


def _llm_judge(ticket: SupportTicket, draft: str) -> float | None:
    try:
        from openai import OpenAI
        api_base = os.environ.get("API_BASE_URL")
        api_key  = os.environ.get("API_KEY")
        if not api_base or not api_key:
            return None
        client = OpenAI(base_url=api_base, api_key=api_key)
        prompt = f"""Score this customer support reply (0-10 each):

Issue: {ticket.subject}
Customer: {ticket.body[:250]}
Reply: {draft}

Criteria:
1. empathy
2. addresses_issue
3. next_steps
4. professional
5. personalization

JSON only: {{"empathy":0-10,"addresses_issue":0-10,"next_steps":0-10,"professional":0-10,"personalization":0-10}}"""

        resp = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Strict support quality evaluator. JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=128, temperature=0.0,
        )
        data = json.loads(resp.choices[0].message.content.strip())
        score = (
            data.get("empathy", 5) * 0.25 +
            data.get("addresses_issue", 5) * 0.30 +
            data.get("next_steps", 5) * 0.25 +
            data.get("professional", 5) * 0.10 +
            data.get("personalization", 5) * 0.10
        ) / 10.0
        return _clip(score)
    except Exception:
        return None


def _grade_resolve(ticket, action, step):
    draft = (action.resolution_draft or "").strip()
    if not draft:
        return _clip(0.05), {"reason": "No draft", "task_complete": step >= 3}

    llm_score = _llm_judge(ticket, draft)
    judge = "llm"

    if llm_score is None:
        judge = "heuristic"
        total = sum(w for _, (w, fn) in RUBRIC.items() if fn(draft, ticket) else 0 for _ in [None])
        total = 0.0
        for _, (w, fn) in RUBRIC.items():
            if fn(draft, ticket):
                total += w
        penalty = max(0, (step - 1) * 0.03)
        llm_score = _clip(max(0.05, total - penalty))

    return llm_score, {
        "judge": judge,
        "score": llm_score,
        "word_count": len(draft.split()),
        "task_complete": llm_score >= 0.65 or step >= 3,
    }
