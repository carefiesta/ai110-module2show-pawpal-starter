"""Basic checks for completing a task and counting tasks on a pet."""

from pawpal_system import Owner, Pet, Task


def test_mark_complete_sets_flag():
    """mark_complete flips a task from open to done."""
    task = Task("Morning walk", "08:00", "daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    """Adding tasks grows the pet's task list by one each time."""
    pet = Pet("Milo", "cat", age=2)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Brush fur", "09:30", "weekly"))
    pet.add_task(Task("Playtime", "17:00", "once"))
    assert len(pet.tasks) == 2


def test_owner_all_tasks_counts_every_pet():
    """all_tasks includes tasks from each pet the owner cares for."""
    owner = Owner("Alex")
    luna = Pet("Luna", "dog")
    milo = Pet("Milo", "cat")
    luna.add_task(Task("Morning walk", "08:00"))
    milo.add_task(Task("Brush fur", "09:30"))
    milo.add_task(Task("Dinner", "18:00"))
    owner.add_pet(luna)
    owner.add_pet(milo)
    assert len(owner.all_tasks()) == 3
