# SupportTicketEnv — OpenEnv Environment

A **real-world** customer support ticket resolution environment where an AI agent
learns to classify, prioritise, and resolve support tickets.

---

## Why this environment?

Every company receives hundreds of support tickets daily. Agents must:
1. Understand what the ticket is about (classification)
2. Decide how urgent it is and who should handle it (prioritisation)
3. Write a helpful, empathetic reply (resolution)

This maps cleanly to three tasks of increasing difficulty with clear, measurable rewards.

---

## Quick start

```bash
git clone <repo>
cd openenv-support
pip install -r requirements.txt

# Run baseline inference
python inference.py --seed 42 --tickets 20

# Start the API server
uvicorn app:app --port 7860
```

Or with Docker:
```bash
docker build -t support-env .
docker run -p 7860:7860 support-env
```

---

## API (OpenEnv spec)

### `POST /reset`
Start a new episode.
```json
{"task_id": "task_classify", "seed": 42}
```
Returns an `Observation`.

### `POST /step`
Submit an action. Returns `(observation, reward, done, info)`.
```json
{
  "category": "billing",
  "priority": "high",
  "assigned_department": "billing_team",
  "resolution_draft": "Dear Priya, ...",
  "reasoning": "Double-charge complaint → billing"
}
```

### `GET /state`
Returns the full `EnvironmentState` snapshot.

### `GET /tasks`
Lists all tasks with difficulty, description, and score range.

---

## Tasks

| Task | Difficulty | Action Fields | Max Steps | Reward |
|------|-----------|---------------|-----------|--------|
| `task_classify` | Easy | `category` | 1 | 0.0 – 1.0 |
| `task_prioritize` | Medium | `priority` + `assigned_department` | 1 | 0.0 – 1.0 |
| `task_resolve` | Hard | `resolution_draft` | 3 | 0.0 – 1.0 |

---

## Observation space

```python
{
  "ticket": {
    "ticket_id":       str,
    "subject":         str,
    "body":            str,
    "customer_name":   str,
    "customer_email":  str,
    "created_at":      str  # ISO-8601
  },
  "task_id":           str,   # task_classify | task_prioritize | task_resolve
  "task_description":  str,
  "step_number":       int,
  "max_steps":         int,
  "instructions":      str
}
```

## Action space

```python
{
  "category":             str | None,  # billing|technical|account|shipping|general
  "priority":             str | None,  # low|medium|high|urgent
  "assigned_department":  str | None,  # billing_team|tech_support|account_management|logistics|general_support
  "resolution_draft":     str | None,  # customer-facing reply
  "reasoning":            str | None   # optional chain-of-thought
}
```

---

## Reward function

### Task 1 — Classify
| Result | Reward |
|--------|--------|
| Exact category match | 1.0 |
| Adjacent category (e.g. billing↔account) | 0.5 |
| Wrong category (but structured) | 0.1 |
| No category provided | 0.0 |

### Task 2 — Prioritise
Weighted average: **0.5 × priority_score + 0.5 × department_score**

Each sub-score uses the same exact/adjacent/wrong/missing scale.

### Task 3 — Resolve
Rubric-based scoring across 6 criteria:

| Criterion | Weight | Signal |
|-----------|--------|--------|
| Greeting by name | 0.10 | Customer first name in draft |
| Acknowledgement | 0.20 | Empathy keywords (sorry, understand…) |
| Solution content | 0.35 | ≥40 words present |
| Concrete next step | 0.20 | Action keywords (will, refund, send…) |
| Polite closing | 0.10 | Closing keywords (regards, thank…) |
| Length (≥80 words) | 0.05 | Word count |

Step penalty: −0.05 × (step − 1) to reward early completion.

---

## Baseline scores (seed=42, 20 episodes each)

```
task_classify      0.795  ███████████████
task_prioritize    0.763  ███████████████
task_resolve       1.000  ████████████████████
```

Baseline uses keyword heuristics and a template reply — no LLM required.

---

## Python usage example

```python
from env.environment import SupportTicketEnv
from env.models import TaskID, TicketAction, Category

env = SupportTicketEnv()

# Task 1 — Classify
obs = env.reset(task_id=TaskID.CLASSIFY, seed=42)
print(obs.ticket.subject)

result = env.step(TicketAction(category=Category.BILLING))
print(f"Reward: {result.reward}, Done: {result.done}")

# Task 3 — Resolve (multi-step)
obs = env.reset(task_id=TaskID.RESOLVE, seed=42)
result = env.step(TicketAction(
    resolution_draft="Dear Priya, I sincerely apologise for the inconvenience. "
                     "I can see you were charged twice. I will process a full refund "
                     "of $29.99 within 3–5 business days. Please don't hesitate to "
                     "reach out if you have any questions. Best regards, Support Team"
))
print(f"Reward: {result.reward}")  # ~0.95
```

---

## Project structure

```
openenv-support/
├── env/
│   ├── models.py         # Pydantic typed models
│   ├── environment.py    # SupportTicketEnv (step/reset/state)
│   └── ticket_bank.py    # 20 realistic support tickets
├── graders/
│   └── grader.py         # Scoring logic with partial credit
├── app.py                # FastAPI HTTP wrapper
├── inference.py          # Baseline agent + reproducible scores
├── openenv.yaml          # OpenEnv spec
├── Dockerfile            # HF Spaces deployment
├── requirements.txt
└── README.md
```

---

## Deployment (Hugging Face Spaces)

1. Create a new Space → SDK: **Docker**
2. Push this repository
3. The Space will auto-build and expose the API at `https://<your-space>.hf.space`

---

## License

MIT
