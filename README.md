# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.


## Sample Output

```
Owner: Jordan  |  Time budget: 90 min
Today's Schedule
====================================================
  TIME   PET       TASK               PRIORITY
  ------ --------- ------------------ --------
  08:00  Mochi     Meds               high
  08:05  Mochi     Feeding            high
  08:15  Biscuit   Morning walk       high
  08:45  Mochi     Play/enrichment    medium
Why this plan:
Plan uses 65 of 90 available minutes starting at 08:00.
Included (ordered by priority, then shortest first):
  Included 'Meds' for Mochi (high priority) at 08:00 - 5 min
  Included 'Feeding' for Mochi (high priority) at 08:05 - 10 min
  Included 'Morning walk' for Biscuit (high priority) at 08:15 - 30 min
  Included 'Play/enrichment' for Mochi (medium priority) at 08:45 - 20 min
Skipped:
  Skipped 'Grooming' for Biscuit - not enough time remaining
```

## Test Results

```
7 passed in 0.05s
```
## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

- **Sorting by time** — `Scheduler.sort_by_time()` sorts tasks by their `preferred_time` (HH:MM), pushing untimed tasks to the end.
- **Filtering** — `Scheduler.filter_tasks()` filters tasks by pet name and/or completion status, independently or combined.
- **Recurring tasks** — `Task.mark_complete()` automatically creates the next occurrence for "daily" (+1 day) and "weekly" (+7 days) tasks, re-adding it to the pet's task list. "Once" tasks create no new instance.
- **Conflict detection** — `Scheduler.detect_conflicts()` flags tasks scheduled at the exact same `preferred_time`, returning warning messages instead of crashing. Known limitation: it checks exact time matches only, not overlapping durations.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
