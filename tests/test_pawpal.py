"""Tests for PawPal+ core behaviors: tasks, pets, and scheduling."""

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete():
    """mark_complete() flips a task's completed flag to True."""
    task = Task("Feeding", 10, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    """Adding a task to a pet increases its task count by one."""
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Meds", 5, priority="high"))
    assert len(pet.tasks) == 1


def test_sort_tasks_orders_by_priority_then_duration():
    """sort_tasks() ranks high priority first, then shorter duration as tiebreaker."""
    walk = Task("Walk", 30, priority="high")
    meds = Task("Meds", 5, priority="high")
    play = Task("Play", 20, priority="medium")
    scheduler = Scheduler()
    ordered = scheduler.sort_tasks([walk, play, meds])
    # Both high-priority tasks come first; among them the shorter (meds) leads.
    assert [t.title for t in ordered] == ["Meds", "Walk", "Play"]


def test_generate_plan_respects_time_budget():
    """generate_plan() includes only tasks that fit and records the rest as skipped."""
    scheduler = Scheduler(available_minutes=40, start_time="08:00")
    tasks = [
        Task("Walk", 30, priority="high"),
        Task("Feeding", 10, priority="high"),
        Task("Grooming", 45, priority="low"),  # too big to fit in 40 min
    ]
    plan = scheduler.generate_plan(tasks)

    titles = [item.title for item in plan]
    assert "Grooming" not in titles
    assert set(titles) == {"Walk", "Feeding"}
    # Both are high priority, so the shorter task (Feeding) is placed first;
    # start times are computed sequentially from start_time.
    assert [item.title for item in plan] == ["Feeding", "Walk"]
    assert plan[0].start_time == "08:00"   # Feeding, 10 min
    assert plan[1].start_time == "08:10"   # Walk starts after Feeding
    # The oversized task is reported as skipped.
    assert any(task.title == "Grooming" for _pet, task, _reason in scheduler.skipped)


def test_edit_task_updates_and_raises_on_bad_id():
    """edit_task() updates matching fields by id and raises on an unknown id."""
    pet = Pet(name="Biscuit", species="dog")
    task = Task("Walk", 30, priority="low")
    pet.add_task(task)

    pet.edit_task(task.id, priority="high", duration_minutes=25)
    assert task.priority == "high"
    assert task.duration_minutes == 25

    with pytest.raises(ValueError):
        pet.edit_task(999999, priority="high")


def test_remove_task_removes_and_raises_on_bad_id():
    """remove_task() drops the task by id and raises on an unknown id."""
    pet = Pet(name="Biscuit", species="dog")
    task = Task("Walk", 30)
    pet.add_task(task)

    pet.remove_task(task.id)
    assert len(pet.tasks) == 0

    with pytest.raises(ValueError):
        pet.remove_task(task.id)


def test_owner_get_all_tasks_flattens_across_pets():
    """get_all_tasks() returns (pet, task) pairs spanning every pet."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Mochi", species="cat")
    dog.add_task(Task("Walk", 30))
    cat.add_task(Task("Feeding", 10))
    cat.add_task(Task("Meds", 5))
    owner.add_pet(dog)
    owner.add_pet(cat)

    pairs = owner.get_all_tasks()
    assert len(pairs) == 3
    assert all(isinstance(p, Pet) and isinstance(t, Task) for p, t in pairs)
