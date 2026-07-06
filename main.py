"""PawPal+ CLI demo.

Builds a small owner/pet/task setup, generates today's plan, and prints it
along with the scheduler's reasoning.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a demo owner with two pets and a spread of care tasks."""
    owner = Owner(name="Jordan", email="jordan@example.com", available_minutes=90)

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=4)
    biscuit.add_task(Task("Morning walk", 30, priority="high", category="walk"))
    biscuit.add_task(Task("Grooming", 45, priority="low", category="grooming"))

    mochi = Pet(name="Mochi", species="cat", breed="Tabby", age=2)
    mochi.add_task(Task("Feeding", 10, priority="high", category="feeding"))
    mochi.add_task(Task("Meds", 5, priority="high", category="meds"))
    mochi.add_task(Task("Play/enrichment", 20, priority="medium", category="enrichment"))

    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    return owner


def print_schedule(plan) -> None:
    """Print a clean, column-aligned 'Today's Schedule' table."""
    print("Today's Schedule")
    print("=" * 52)
    if not plan:
        print("  (nothing scheduled)")
        return
    print(f"  {'TIME':<6} {'PET':<9} {'TASK':<18} {'PRIORITY'}")
    print(f"  {'-' * 6} {'-' * 9} {'-' * 18} {'-' * 8}")
    for item in plan:
        print(
            f"  {item.start_time:<6} {item.pet_name:<9} {item.title:<18} "
            f"{item.priority}"
        )


def _fmt(task) -> str:
    """One-line label for a task, showing its preferred time when set."""
    when = task.preferred_time or "--:--"
    return f"{when}  {task.title:<16} [{task.priority}]"


def demo_sorting(scheduler: Scheduler) -> None:
    """Add tasks out of order and print them sorted by preferred_time."""
    print("=== Sorting Demo (by preferred_time) ===")
    tasks = [
        Task("Evening walk", 30, preferred_time="18:00"),
        Task("Feeding", 10, preferred_time="08:00"),
        Task("Vet reminder", 5),  # no preferred_time -> should sort last
        Task("Meds", 5, preferred_time="12:30"),
    ]
    print("Input order: ", [t.title for t in tasks])
    for t in scheduler.sort_by_time(tasks):
        print("  " + _fmt(t))
    print()


def demo_filtering(owner: Owner, scheduler: Scheduler) -> None:
    """Show filter_tasks() by pet name and by completion status."""
    print("=== Filtering Demo ===")
    pairs = owner.get_all_tasks()

    biscuit_only = scheduler.filter_tasks(pairs, pet_name="Biscuit")
    print("Filter by pet_name='Biscuit':")
    for pet, task in biscuit_only:
        print(f"  {pet.name}: {task.title}")

    # Mark one task complete to demonstrate the completion filter.
    mochi = next(p for p in owner.list_pets() if p.name == "Mochi")
    mochi.tasks[0].mark_complete()
    incomplete = scheduler.filter_tasks(pairs, completed=False)
    print("Filter by completed=False (across all pets):")
    for pet, task in incomplete:
        print(f"  {pet.name}: {task.title}")
    print()


def demo_recurring() -> None:
    """Mark a daily task complete and show the auto-created next occurrence."""
    print("=== Recurring Task Demo ===")
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task("Morning walk", 30, priority="high", recurrence="daily"))
    task_id = pet.tasks[0].id

    print(f"Before: {len(pet.tasks)} task(s); '{pet.tasks[0].title}' completed="
          f"{pet.tasks[0].completed}")
    new_task = pet.complete_task(task_id)
    print(f"Completed the daily task -> new instance created: {new_task is not None}")
    if new_task:
        print(f"  New task: '{new_task.title}' | completed={new_task.completed} "
              f"| due_date={new_task.due_date} | id differs={new_task.id != task_id}")
    print(f"After:  {len(pet.tasks)} task(s) (original completed + next occurrence)")
    print()


def demo_conflicts(scheduler: Scheduler) -> None:
    """Add tasks at the same preferred_time and print detect_conflicts() warnings."""
    print("=== Conflict Detection Demo ===")
    biscuit = Pet(name="Biscuit", species="dog")
    mochi = Pet(name="Mochi", species="cat")
    biscuit.add_task(Task("Morning walk", 30, preferred_time="08:00"))
    mochi.add_task(Task("Meds", 5, preferred_time="08:00"))       # clashes with the walk
    mochi.add_task(Task("Feeding", 10, preferred_time="12:00"))    # no clash

    pairs = [(biscuit, t) for t in biscuit.tasks] + [(mochi, t) for t in mochi.tasks]
    warnings = scheduler.detect_conflicts(pairs)
    if warnings:
        for w in warnings:
            print("  " + w)
    else:
        print("  No conflicts detected.")
    print("  (Note: exact-time match only; duration overlaps are not detected.)")
    print()


def main() -> None:
    """Run the end-to-end PawPal+ demo."""
    owner = build_demo_owner()
    scheduler = Scheduler(available_minutes=owner.available_minutes, start_time="08:00")

    plan = scheduler.generate_plan(owner.get_all_tasks())
    print(f"Owner: {owner.name}  |  Time budget: {owner.available_minutes} min\n")
    print_schedule(plan)
    print("\nWhy this plan:")
    print(scheduler.explain(plan))
    print()

    demo_sorting(scheduler)
    demo_filtering(owner, scheduler)
    demo_recurring()
    demo_conflicts(scheduler)


if __name__ == "__main__":
    main()
