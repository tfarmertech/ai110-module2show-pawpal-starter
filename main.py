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


def main() -> None:
    """Run the end-to-end PawPal+ demo."""
    owner = build_demo_owner()
    scheduler = Scheduler(available_minutes=owner.available_minutes, start_time="08:00")

    plan = scheduler.generate_plan(owner.get_all_tasks())

    print(f"Owner: {owner.name}  |  Time budget: {owner.available_minutes} min\n")
    print_schedule(plan)
    print("\nWhy this plan:")
    print(scheduler.explain(plan))


if __name__ == "__main__":
    main()
