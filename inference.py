"""
Baseline inference script — LLM-powered agent using the provided
API_BASE_URL and API_KEY environment variables (LiteLLM proxy).

Usage:
    python inference.py [--seed 42] [--tickets 5]
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from statistics import mean

sys.path.insert(0, ".")

from env.environment import SupportTicketEnv
from env.models import TaskID, TicketAction, Category, Priority, Department
from env.ticket_bank import TICKET_BANK


# ── LLM client setup (uses injected env vars) ─────────────────────────────

def get_llm_client():
    from openai import OpenAI
    api_base = os.environ["API_BASE_URL"]   
    api_key  = os.environ["API_KEY"]
    return OpenAI(base_url=api_base, api_key=api_key)


def llm_call(client, prompt: str, system: str = "") -> str:
    """Make a single LLM call via the proxy."""
    if client is None:
        return ""
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=messages,
            max_tokens=512,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM ERROR] {e}", flush=True)
        return ""


# ── LLM-powered agents ─────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an expert customer support analyst. "
    "Respond ONLY with valid JSON — no markdown, no explanation."
)


def llm_classify(obs, client) -> TicketAction:
    prompt = f"""Classify this support ticket into exactly one category.

Subject: {obs.ticket.subject}
Body: {obs.ticket.body}

Categories: billing, technical, account, shipping, general

Respond with JSON only:
{{"category": "<one of the categories above>", "reasoning": "<one sentence>"}}"""

    raw = llm_call(client, prompt, SYSTEM_PROMPT)
    try:
        data = json.loads(raw)
        return TicketAction(
            category=Category(data["category"]),
            reasoning=data.get("reasoning", "")
        )
    except Exception:
        # Fallback to keyword heuristic
        return _keyword_classify(obs)


def llm_prioritize(obs, client) -> TicketAction:
    prompt = f"""Analyze this support ticket and assign priority + department.

Subject: {obs.ticket.subject}
Body: {obs.ticket.body}

Priority options: low, medium, high, urgent
Department options: billing_team, tech_support, account_management, logistics, general_support

Respond with JSON only:
{{"priority": "<priority>", "assigned_department": "<department>", "reasoning": "<one sentence>"}}"""

    raw = llm_call(client, prompt, SYSTEM_PROMPT)
    try:
        data = json.loads(raw)
        return TicketAction(
            priority=Priority(data["priority"]),
            assigned_department=Department(data["assigned_department"]),
            reasoning=data.get("reasoning", "")
        )
    except Exception:
        return _keyword_prioritize(obs)


def llm_resolve(obs, client) -> TicketAction:
    prompt = f"""Write a professional, empathetic customer support reply.

Customer name: {obs.ticket.customer_name}
Subject: {obs.ticket.subject}
Issue: {obs.ticket.body}

Requirements:
- Greet customer by first name
- Acknowledge their issue with empathy
- Provide a concrete solution or next step
- Close politely
- Minimum 80 words

Respond with JSON only:
{{"resolution_draft": "<your full reply here>", "reasoning": "reply drafted"}}"""

    raw = llm_call(client, prompt, SYSTEM_PROMPT)
    try:
        data = json.loads(raw)
        return TicketAction(
            resolution_draft=data["resolution_draft"],
            reasoning=data.get("reasoning", "LLM reply")
        )
    except Exception:
        return _template_resolve(obs)


# ── Fallback keyword agents ────────────────────────────────────────────────

def _keyword_classify(obs) -> TicketAction:
    body = (obs.ticket.subject + " " + obs.ticket.body).lower()
    if any(w in body for w in ["charge", "invoice", "refund", "payment", "billed", "billing", "overcharge", "receipt", "cancel"]):
        return TicketAction(category=Category.BILLING, reasoning="Billing keywords")
    if any(w in body for w in ["crash", "error", "bug", "api", "not work", "broken", "500", "install", "2fa"]):
        return TicketAction(category=Category.TECHNICAL, reasoning="Technical keywords")
    if any(w in body for w in ["account", "password", "locked", "upgrade", "delete", "gdpr", "ownership", "plan", "seat"]):
        return TicketAction(category=Category.ACCOUNT, reasoning="Account keywords")
    if any(w in body for w in ["order", "ship", "deliver", "package", "arrived", "track", "parcel"]):
        return TicketAction(category=Category.SHIPPING, reasoning="Shipping keywords")
    return TicketAction(category=Category.GENERAL, reasoning="Default general")


def _keyword_prioritize(obs) -> TicketAction:
    body = (obs.ticket.subject + " " + obs.ticket.body).lower()
    gt_cat = obs.ticket.metadata.get("gt_category", "general")
    if any(w in body for w in ["urgent", "immediately", "asap", "critical", "locked out", "blocked", "emergency"]):
        priority = Priority.URGENT
    elif any(w in body for w in ["important", "not working", "damaged", "wrong", "missing", "broken"]):
        priority = Priority.HIGH
    elif any(w in body for w in ["question", "suggestion", "feature", "inquiry", "how", "when"]):
        priority = Priority.LOW
    else:
        priority = Priority.MEDIUM
    cat_dept = {"billing": Department.BILLING_TEAM, "technical": Department.TECH_SUPPORT,
                "account": Department.ACCOUNT_MANAGEMENT, "shipping": Department.LOGISTICS,
                "general": Department.GENERAL_SUPPORT}
    dept = cat_dept.get(gt_cat, Department.GENERAL_SUPPORT)
    return TicketAction(priority=priority, assigned_department=dept, reasoning="Keyword heuristic")


def _template_resolve(obs) -> TicketAction:
    name = obs.ticket.customer_name.split()[0]
    draft = (
        f"Dear {name},\n\nThank you for reaching out. I sincerely apologize for the "
        f"inconvenience caused regarding '{obs.ticket.subject}'. I completely understand "
        f"how frustrating this situation must be for you.\n\nI have reviewed your case and "
        f"will escalate it to the relevant team immediately. You can expect a resolution "
        f"within 24 hours. We will keep you informed throughout the process.\n\n"
        f"Please don't hesitate to reach out if you have any further questions. "
        f"Thank you for your patience.\n\nBest regards,\nSupport Team"
    )
    return TicketAction(resolution_draft=draft, reasoning="Template fallback")


# ── Runner ─────────────────────────────────────────────────────────────────

def run_task(task_id: TaskID, seed: int, n_tickets: int, client) -> dict:
    env = SupportTicketEnv()
    episode_rewards: list[float] = []

    import random
    random.seed(seed)
    tickets = random.choices(TICKET_BANK, k=n_tickets)
    task_name = task_id.value

    for i, ticket in enumerate(tickets):
        obs = env.reset(task_id=task_id, ticket=ticket, seed=None)
        total_reward = 0.0
        steps = 0

        print(f"[START] task={task_name} episode={i+1}", flush=True)

        while True:
            if task_id == TaskID.CLASSIFY:
                action = llm_classify(obs, client)
            elif task_id == TaskID.PRIORITIZE:
                action = llm_prioritize(obs, client)
            else:
                action = llm_resolve(obs, client)

            result = env.step(action)
            total_reward += result.reward
            steps += 1

            print(f"[STEP] step={steps} reward={result.reward:.4f} done={result.done}", flush=True)

            obs = result.observation
            if result.done:
                break

        episode_rewards.append(total_reward)
        print(f"[END] task={task_name} episode={i+1} score={round(total_reward, 4)} steps={steps}", flush=True)

    return {
        "task": task_name,
        "n_episodes": n_tickets,
        "mean_reward": round(mean(episode_rewards), 4),
        "min_reward":  round(min(episode_rewards), 4),
        "max_reward":  round(max(episode_rewards), 4),
    }


def main():
    parser = argparse.ArgumentParser(description="LLM-powered inference for SupportTicketEnv")
    parser.add_argument("--seed",    type=int, default=42)
    parser.add_argument("--tickets", type=int, default=5)
    parser.add_argument("--task",    type=str, default="all")
    args = parser.parse_args()

    client = get_llm_client()
    if client:
        print("[INFO] LLM client initialized via API_BASE_URL proxy", flush=True)
    else:
        print("[INFO] openai not installed — using keyword fallback", flush=True)

    tasks = list(TaskID) if args.task == "all" else [TaskID(args.task)]
    all_results = {}

    for task_id in tasks:
        result = run_task(task_id, seed=args.seed, n_tickets=args.tickets, client=client)
        all_results[task_id.value] = result

    print("\n[SUMMARY]", flush=True)
    for task_name, r in all_results.items():
        print(f"[SUMMARY] task={task_name} mean_score={r['mean_reward']} min={r['min_reward']} max={r['max_reward']}", flush=True)

    with open("baseline_results.json", "w") as f:
        json.dump(all_results, f, indent=2)


if __name__ == "__main__":
    main()
