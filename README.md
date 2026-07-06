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

### Sample test run

```
$ python -m pytest -v
================================================= test session starts =================================================
platform win32 -- Python 3.13.3, pytest-9.1.1, pluggy-1.6.0
collected 20 items

tests/test_pawpal.py::test_mark_complete PASSED                                                                  [  5%]
tests/test_pawpal.py::test_add_task_increases_count PASSED                                                       [ 10%]
tests/test_pawpal.py::test_sort_tasks_orders_by_priority_then_duration PASSED                                    [ 15%]
tests/test_pawpal.py::test_generate_plan_respects_time_budget PASSED                                             [ 20%]
tests/test_pawpal.py::test_edit_task_updates_and_raises_on_bad_id PASSED                                         [ 25%]
tests/test_pawpal.py::test_remove_task_removes_and_raises_on_bad_id PASSED                                       [ 30%]
tests/test_pawpal.py::test_owner_get_all_tasks_flattens_across_pets PASSED                                       [ 35%]
tests/test_pawpal.py::test_sort_by_time_puts_untimed_tasks_last PASSED                                           [ 40%]
tests/test_pawpal.py::test_filter_tasks_by_pet_and_completion PASSED                                             [ 45%]
tests/test_pawpal.py::test_mark_complete_creates_next_daily_occurrence PASSED                                    [ 50%]
tests/test_pawpal.py::test_mark_complete_once_creates_nothing PASSED                                             [ 55%]
tests/test_pawpal.py::test_complete_task_readds_recurring_instance_to_pet PASSED                                 [ 60%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time_and_ignores_untimed PASSED                           [ 65%]
tests/test_pawpal.py::test_pet_with_zero_tasks_does_not_crash PASSED                                             [ 70%]
tests/test_pawpal.py::test_sort_by_time_all_untimed_no_crash PASSED                                              [ 75%]
tests/test_pawpal.py::test_detect_conflicts_same_pet_same_time PASSED                                            [ 80%]
tests/test_pawpal.py::test_detect_conflicts_same_and_cross_pet_at_one_time PASSED                                [ 85%]
tests/test_pawpal.py::test_filter_and_detect_on_empty_list_return_empty PASSED                                   [ 90%]
tests/test_pawpal.py::test_complete_task_once_adds_no_new_task PASSED                                            [ 95%]
tests/test_pawpal.py::test_mark_complete_creates_next_weekly_occurrence PASSED                                   [100%]

================================================== 20 passed in 0.05s ==================================================
```
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
