"""Command-line demo of a PawPal+ daily schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create an owner, two pets, and three tasks at different times."""
    owner = Owner(name="Alex")
    luna = Pet(name="Luna", species="dog", age=4)
    milo = Pet(name="Milo", species="cat", age=2)
    luna.add_task(Task("Dinner", "18:00", "daily"))
    luna.add_task(Task("Morning walk", "08:00", "daily"))
    milo.add_task(Task("Brush fur", "09:30", "weekly"))
    owner.add_pet(luna)
    owner.add_pet(milo)
    return owner


def main() -> None:
    """Print today's care list for the demo household."""
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    print(f"Today's Schedule for {owner.name}")
    print(f"Pets: {len(owner.pets)}    Tasks: {len(owner.all_tasks())}")
    print()
    for pet, task in scheduler.todays_schedule():
        status = "done" if task.completed else "open"
        print(
            f"{task.time}  {pet.name} ({pet.species}) — {task.description} "
            f"[{task.frequency}, {status}]"
        )


if __name__ == "__main__":
    main()
