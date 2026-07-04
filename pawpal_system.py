"""PawPal+ system scaffolding.

Class skeletons only — no scheduling logic yet. See diagrams/uml.mmd.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, enrichment, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"          # "low" | "medium" | "high"
    recurrence: str = "daily"         # "daily" | "weekly" | "once"
    category: str = "general"
    preferred_time: str | None = None  # e.g. "08:00"
    completed: bool = False

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (for sorting)."""
        ...

    def is_due_today(self, weekday: int) -> bool:
        """Return True if this task should appear in today's plan."""
        ...


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
        ...

    def edit_task(self, title: str, **changes) -> None:
        """Update fields on the task matching `title`."""
        ...

    def remove_task(self, title: str) -> None:
        """Remove the task matching `title`."""
        ...


class Owner:
    """The pet owner: contact info, daily time budget, preferences, and pets."""

    def __init__(
        self,
        name: str,
        email: str = "",
        available_minutes: int = 120,
        preferences: dict | None = None,
    ) -> None:
        self.name = name
        self.email = email
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        ...

    def remove_pet(self, name: str) -> None:
        """Remove the pet matching `name`."""
        ...

    def list_pets(self) -> list[Pet]:
        """Return this owner's pets."""
        ...


class Scheduler:
    """Builds and explains a daily plan from a pet's tasks under time constraints."""

    def __init__(
        self,
        available_minutes: int = 120,
        start_time: str = "08:00",
        preferences: dict | None = None,
    ) -> None:
        self.available_minutes = available_minutes
        self.start_time = start_time
        self.preferences = preferences or {}

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks (e.g. by priority, then duration)."""
        ...

    def generate_plan(self, tasks: list[Task]) -> list:
        """Return an ordered, time-boxed plan that fits the time budget."""
        ...

    def explain(self, plan: list) -> str:
        """Return human-readable reasoning for the produced plan."""
        ...
