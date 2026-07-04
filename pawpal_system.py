"""PawPal+ system implementation.

Domain model and scheduling logic for the PawPal+ pet-care planner.
See diagrams/uml.mmd for the class diagram.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

# Monotonic id source so every Task gets a unique, stable identifier.
_task_ids = itertools.count(1)

# Numeric weights used to rank tasks; higher is more important.
_PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}


def _parse_time(hhmm: str) -> int:
    """Convert an 'HH:MM' clock string into minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _format_time(total_minutes: int) -> str:
    """Convert minutes since midnight into an 'HH:MM' clock string."""
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, enrichment, grooming, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"           # "low" | "medium" | "high"
    recurrence: str = "daily"          # "daily" | "weekly" | "once"
    category: str = "general"
    preferred_time: str | None = None  # e.g. "08:00"
    completed: bool = False
    due_weekday: int | None = None     # 0=Mon..6=Sun; used by "weekly" recurrence
    id: int = field(default_factory=lambda: next(_task_ids))

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (higher = sooner)."""
        return _PRIORITY_WEIGHTS.get(self.priority, 0)

    def is_due_today(self, weekday: int) -> bool:
        """Return True if this task should appear in a plan for the given weekday."""
        if self.recurrence == "daily":
            return True
        if self.recurrence == "weekly":
            return self.due_weekday is None or self.due_weekday == weekday
        if self.recurrence == "once":
            return not self.completed
        return True


@dataclass
class Pet:
    """A pet owned by an Owner, with its own list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def _find_task(self, task_id: int) -> Task:
        """Return the task with the given id, or raise ValueError if absent."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"No task with id {task_id!r} on pet {self.name!r}")

    def edit_task(self, task_id: int, **changes) -> Task:
        """Update fields on the task matching `task_id`; raise if id or field is invalid."""
        task = self._find_task(task_id)
        for key, value in changes.items():
            if not hasattr(task, key):
                raise AttributeError(f"Task has no field {key!r}")
            setattr(task, key, value)
        return task

    def remove_task(self, task_id: int) -> None:
        """Remove the task matching `task_id`; raise ValueError if not found."""
        task = self._find_task(task_id)
        self.tasks.remove(task)


class Owner:
    """The pet owner: contact info, daily time budget, preferences, and pets."""

    def __init__(
        self,
        name: str,
        email: str = "",
        available_minutes: int = 120,
        preferences: dict | None = None,
    ) -> None:
        """Create an owner with a daily time budget and optional preferences."""
        self.name = name
        self.email = email
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the pet matching `name`; raise ValueError if not found."""
        for pet in self.pets:
            if pet.name == name:
                self.pets.remove(pet)
                return
        raise ValueError(f"No pet named {name!r}")

    def list_pets(self) -> list[Pet]:
        """Return this owner's pets."""
        return self.pets

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return a flat list of (pet, task) pairs across all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledItem:
    """One entry in a generated daily plan: a task placed at a start time."""

    start_time: str
    pet_name: str
    title: str
    duration_minutes: int
    priority: str


class Scheduler:
    """Builds and explains a daily plan from tasks under a time budget."""

    def __init__(
        self,
        available_minutes: int = 120,
        start_time: str = "08:00",
        preferences: dict | None = None,
    ) -> None:
        """Create a scheduler with a time budget, a start time, and preferences."""
        self.available_minutes = available_minutes
        self.start_time = start_time
        self.preferences = preferences or {}
        # Populated by generate_plan(); consumed by explain().
        self.skipped: list[tuple[Pet | None, Task, str]] = []

    @staticmethod
    def _normalize(item: Task | tuple[Pet, Task]) -> tuple[Pet | None, Task]:
        """Accept either a Task or a (pet, task) pair and return a (pet, task) pair."""
        if isinstance(item, tuple):
            pet, task = item
            return pet, task
        return None, item

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), then shorter duration as tiebreaker."""
        return sorted(tasks, key=lambda t: (-t.priority_score(), t.duration_minutes))

    def generate_plan(self, tasks) -> list[ScheduledItem]:
        """Build a time-boxed plan that fits the budget, skipping tasks that don't fit.

        Accepts a list of Tasks or (pet, task) pairs. Returns the ordered included
        items; records skipped tasks on ``self.skipped`` for ``explain()``.
        """
        pairs = [self._normalize(item) for item in tasks]
        pairs.sort(key=lambda pt: (-pt[1].priority_score(), pt[1].duration_minutes))

        plan: list[ScheduledItem] = []
        self.skipped = []
        cursor = _parse_time(self.start_time)
        used = 0

        for pet, task in pairs:
            if used + task.duration_minutes <= self.available_minutes:
                plan.append(
                    ScheduledItem(
                        start_time=_format_time(cursor),
                        pet_name=pet.name if pet else "",
                        title=task.title,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                    )
                )
                cursor += task.duration_minutes
                used += task.duration_minutes
            else:
                self.skipped.append((pet, task, "not enough time remaining"))

        return plan

    def explain(self, plan: list[ScheduledItem]) -> str:
        """Return a human-readable, multi-line explanation of the plan's choices."""
        lines: list[str] = []
        total = sum(item.duration_minutes for item in plan)
        lines.append(
            f"Plan uses {total} of {self.available_minutes} available minutes "
            f"starting at {self.start_time}."
        )

        if plan:
            lines.append("Included (ordered by priority, then shortest first):")
            for item in plan:
                who = f" for {item.pet_name}" if item.pet_name else ""
                lines.append(
                    f"  Included '{item.title}'{who} ({item.priority} priority) "
                    f"at {item.start_time} - {item.duration_minutes} min"
                )
        else:
            lines.append("No tasks fit within the available time.")

        if self.skipped:
            lines.append("Skipped:")
            for pet, task, reason in self.skipped:
                who = f" for {pet.name}" if pet else ""
                lines.append(f"  Skipped '{task.title}'{who} - {reason}")

        return "\n".join(lines)
