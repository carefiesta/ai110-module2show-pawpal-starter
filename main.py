"""Command-line demo of a PawPal+ daily schedule."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create an owner, two pets, and tasks inserted out of clock order."""
    owner = Owner(
        name="Alex",
        available_from="07:00",
        available_until="21:00",
        preferences="Keep evening tasks short.",
    )
    luna = Pet(name="Luna", species="dog", age=4)
    milo = Pet(name="Milo", species="cat", age=2)
    luna.add_task(Task("Dinner", "18:00", "daily", duration_mins=15, priority="high"))
    luna.add_task(Task("Morning walk", "08:00", "daily", duration_mins=30, priority="high"))
    luna.add_task(Task("Meds", "08:15", "daily", duration_mins=10, priority="high"))
    milo.add_task(Task("Brush fur", "09:30", "weekly", duration_mins=20, priority="medium"))
    milo.add_task(Task("Late-night check", "23:00", "once", duration_mins=10, priority="low"))
    owner.add_pet(luna)
    owner.add_pet(milo)
    return owner


def main() -> None:
    """Print a sorted plan, a conflict warning, filters, and a repeat."""
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    today = date.today().isoformat()
    print(f"Today's Schedule for {owner.name} ({today})")
    print(f"Owner note: {owner.preferences}")
    print(f"Available hours: {owner.available_from}-{owner.available_until}")
    print()
    plan = scheduler.todays_schedule()
    if not plan:
        print("No open tasks for today.")
    for index, (pet, task) in enumerate(plan):
        print(
            f"{task.time}  {pet.name} ({pet.species}) — {task.description} "
            f"({task.duration_mins} min, {task.priority} priority, {task.frequency})"
        )
        print(f"    Why: {scheduler.explain(task, index)}")
    print()
    warnings = scheduler.conflict_warnings()
    if warnings:
        print("Conflicts:")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("No scheduling conflicts.")
    print()
    milo_tasks = scheduler.filter_by_pet("Milo")
    milo_bits = ", ".join(f"{task.time} {task.description}" for task in milo_tasks)
    print(f"filter_by_pet('Milo'): {milo_bits}")
    print(f"filter_by_status(open): {len(scheduler.filter_by_status(False))} task(s)")
    print()
    luna = owner.pets[0]
    walk = next(task for task in luna.tasks if task.description == "Morning walk")
    upcoming = scheduler.complete_task(luna, walk)
    print(f"Completed '{walk.description}' on {walk.due_date.isoformat()}.")
    if upcoming is not None:
        print(f"Next instance: {upcoming.due_date.isoformat()} at {upcoming.time} ({upcoming.frequency}).")


if __name__ == "__main__":
    main()