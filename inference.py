"""
Baseline inference script — runs a rule-based agent across all 3 tasks
and reports reproducible scores with required [START]/[STEP]/[END] blocks.

Usage:
    python inference.py [--seed 42] [--tickets 20]
"""

from __future__ import annotations
import argparse
import json
import sys
from statistics import mean

sys.path.insert(0, ".")

from env.environment import SupportTicketEnv
from env.models import TaskID, TicketAction, Category, Priority, Department
from env.ticket_bank import TICKET_BANK


# ── Baseline agents (rule-based, no LLM) ─────────────────────────────────

def baseline_classify(obs) -> TicketAction:
    body = (obs.ticket.subject + " " + obs.ticket.body).lower()
    if any(w in body for w in ["charge", "invoice", "refund", "payment", "billed", "billing", "overcharge", "receipt", "cancel"]):
        return TicketAction(category=Category.BILLING, reasoning="Billing keywords detected")
    if any(w in body for w in ["crash", "error", "bug", "api", "login fail", "not work", "broken", "500", "install", "export", "2fa", "screen reader"]):
        return TicketAction(category=Category.TECHNICAL, reasoning="Technical keywords detected")
    if any(w in body for w in ["account", "password", "locked", "upgrade", "delete", "gdpr", "ownership", "plan", "seat", "transfer"]):
        return TicketAction(category=Category.ACCOUNT, reasoning="Account keywords detected")
    if any(w in body for w in ["order", "ship", "deliver", "package", "arrived", "track", "custom", "parcel", "wrong item"]):
        return TicketAction(category=Category.SHIPPING, reasoning="Shipping keywords detected")
    return TicketAction(category=Category.GENERAL, reasoning="No strong signal — defaulting to general")


def baseline_prioritize(obs) -> TicketAction:
    body = (obs.ticket.subject + " " + obs.ticket.body).lower()
    gt_cat = obs.ticket.metadata.get("gt_category", "general")

    if any(w in body for w in ["urgent", "immediately", "asap", "critical", "locked out", "blocked", "emergency", "hours"]):
        priority = Priority.URGENT
    elif any(w in body for w in ["important", "please fix", "not working", "damaged", "wrong", "missing", "overcharge", "broken", "3 days", "weeks"]):
        priority = Priority.HIGH
    elif any(w in body for w in ["question", "suggestion", "feature", "inquiry", "how", "when", "plan"]):
        priority = Priority.LOW
    else:
        priority = Priority.MEDIUM

    cat_dept_map = {
        "billing":   Department.BILLING_TEAM,
        "technical": Department.TECH_SUPPORT,
        "account":   Department.ACCOUNT_MANAGEMENT,
        "shipping":  Department.LOGISTICS,
        "general":   Department.GENERAL_SUPPORT,
    }
    dept = cat_dept_map.get(gt_cat, Department.GENERAL_SUPPORT)
    return TicketAction(priority=priority, assigned_department=dept, reasoning="Keyword-based heuristic")


def baseline_resolve(obs) -> TicketAction:
    t = obs.ticket
    name = t.customer_name.split()[0]
    draft = (
        f"Dear {name},\n\n"
        f"Thank you for reaching out to us. I'm sorry to hear about the "
        f"issue you're experiencing regarding '{t.subject}'. "
        f"I completely understand how frustrating this must be for you, "
        f"and I want to assure you that we take this seriously.\n\n"
        f"I have reviewed your request and will escalate this to the relevant "
        f"team immediately. You can expect an update from us within 24 hours. "
        f"We will work to resolve this as quickly as possible and keep you "
        f"informed throughout the process.\n\n"
        f"If you have any additional information or questions in the meantime, "
        f"please don't hesitate to reach out. Thank you for your patience.\n\n"
        f"Best regards,\nSupport Team"
    )
    return TicketAction(resolution_draft=draft, reasoning="Template-based reply")


BASELINE_AGENTS = {
    TaskID.CLASSIFY:   baseline_classify,
    TaskID.PRIORITIZE: baseline_prioritize,
    TaskID.RESOLVE:    baseline_resolve,
}


# ── Runner ─────────────────────────────────────────────────────────────────

def run_task(task_id: TaskID, seed: int, n_tickets: int) -> dict:
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

        # [START] block
        print(f"[START] task={task_name} episode={i+1}", flush=True)

        while True:
            agent_fn = BASELINE_AGENTS[task_id]
            action = agent_fn(obs)
            result = env.step(action)
            total_reward += result.reward
            steps += 1

            # [STEP] block
            print(f"[STEP] step={steps} reward={result.reward:.4f} done={result.done}", flush=True)

            obs = result.observation
            if result.done:
                break

        episode_rewards.append(total_reward)

        # [END] block
        print(f"[END] task={task_name} episode={i+1} score={round(total_reward, 4)} steps={steps}", flush=True)

    return {
        "task": task_name,
        "n_episodes": n_tickets,
        "mean_reward": round(mean(episode_rewards), 4),
        "min_reward":  round(min(episode_rewards), 4),
        "max_reward":  round(max(episode_rewards), 4),
    }


def main():
    parser = argparse.ArgumentParser(description="Baseline inference for SupportTicketEnv")
    parser.add_argument("--seed",    type=int, default=42, help="Random seed")
    parser.add_argument("--tickets", type=int, default=20, help="Episodes per task")
    parser.add_argument("--task",    type=str, default="all",
                        help="task_classify | task_prioritize | task_resolve | all")
    args = parser.parse_args()

    tasks = (
        list(TaskID)
        if args.task == "all"
        else [TaskID(args.task)]
    )

    all_results = {}

    for task_id in tasks:
        result = run_task(task_id, seed=args.seed, n_tickets=args.tickets)
        all_results[task_id.value] = result

    # Summary
    print("\n[SUMMARY]", flush=True)
    for task_name, r in all_results.items():
        print(f"[SUMMARY] task={task_name} mean_score={r['mean_reward']} min={r['min_reward']} max={r['max_reward']}", flush=True)

    with open("baseline_results.json", "w") as f:
        json.dump(all_results, f, indent=2)


if __name__ == "__main__":
    main()