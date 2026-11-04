"""Checks for task records and for the scheduling rules."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_sort_by_time_orders_earliest_first():
    """sort_by_time orders by HH:MM and does not reorder the pet's own list."""
    pet = Pet("Luna", "dog")
    pet.add_task(Task("Dinner", "18:00"))
    pet.add_task(Task("Walk", "08:00"))
    pet.add_task(Task("Meds", "12:30"))
    owner = Owner("Sam")
    owner.add_pet(pet)
    ordered = Scheduler(owner).sort_by_time(pet.tasks)
    assert [task.description for task in ordered] == ["Walk", "Meds", "Dinner"]
    assert [task.description for task in pet.tasks] == ["Dinner", "Walk", "Meds"]


def test_todays_schedule_is_sorted_and_skips_other_days():
    """The daily plan is in clock order and only includes the requested date."""
    day = date(2026, 11, 4)
    pet = Pet("Luna", "dog")
    pet.add_task(Task("Dinner", "18:00", due_date=day))
    pet.add_task(Task("Walk", "08:00", due_date=day))
    pet.add_task(Task("Tomorrow meds", "07:00", due_date=date(2026, 11, 5)))
    owner = Owner("Sam")
    owner.add_pet(pet)
    plan = Scheduler(owner).todays_schedule(day)
    assert [task.description for _, task in plan] == ["Walk", "Dinner"]


def test_daily_task_spawns_the_next_day():
    """Completing a daily task adds one new instance one day later."""
    pet = Pet("Luna", "dog")
    task = Task("Breakfast", "07:00", frequency="daily", due_date=date(2026, 11, 4))
    pet.add_task(task)
    owner = Owner("Sam")
    owner.add_pet(pet)
    upcoming = Scheduler(owner).complete_task(pet, task)
    assert task.completed is True
    assert upcoming is not None
    assert upcoming.due_date == date(2026, 11, 5)
    assert upcoming.time == "07:00"
    assert upcoming.completed is False
    assert upcoming in pet.tasks
    assert len(pet.tasks) == 2


def test_weekly_task_spawns_seven_days_later():
    """Completing a weekly task adds a copy seven days ahead."""
    pet = Pet("Milo", "cat")
    task = Task(
        "Brush fur",
        "09:30",
        frequency="weekly",
        duration_mins=20,
        priority="medium",
        due_date=date(2026, 11, 4),
    )
    pet.add_task(task)
    owner = Owner("Sam")
    owner.add_pet(pet)
    upcoming = Scheduler(owner).complete_task(pet, task)
    assert upcoming is not None
    assert upcoming.due_date == date(2026, 11, 11)
    assert upcoming.time == "09:30"
    assert upcoming.duration_mins == 20
    assert upcoming.priority == "medium"
    assert upcoming.completed is False


def test_once_task_does_not_repeat():
    """A one-time task is marked done and does not create another task."""
    pet = Pet("Luna", "dog")
    task = Task("Bath", "15:00", frequency="once", due_date=date(2026, 11, 4))
    pet.add_task(task)
    owner = Owner("Sam")
    owner.add_pet(pet)
    upcoming = Scheduler(owner).complete_task(pet, task)
    assert upcoming is None
    assert task.completed is True
    assert len(pet.tasks) == 1


def test_completing_twice_does_not_add_another_copy():
    """A second complete call on a daily task does not spawn a third copy."""
    pet = Pet("Luna", "dog")
    task = Task("Breakfast", "07:00", frequency="daily", due_date=date(2026, 11, 4))
    pet.add_task(task)
    scheduler = Scheduler(Owner("Sam"))
    scheduler.owner.add_pet(pet)
    scheduler.complete_task(pet, task)
    again = scheduler.complete_task(pet, task)
    assert again is None
    assert len(pet.tasks) == 2


def test_overlap_returns_a_warning():
    """A task that starts during another open task produces a warning."""
    day = date(2026, 11, 4)
    pet = Pet("Luna", "dog")
    pet.add_task(Task("Morning walk", "08:00", duration_mins=30, due_date=day))
    owner = Owner("Sam")
    owner.add_pet(pet)
    meds = Task("Meds", "08:15", duration_mins=10, due_date=day)
    warning = Scheduler(owner).check_conflicts(meds)
    assert warning.startswith("Warning:")
    assert "overlaps" in warning
    assert "Morning walk" in warning
    assert "Meds" in warning


def test_back_to_back_tasks_do_not_conflict():
    """A task that starts when the previous one ends is not an overlap."""
    day = date(2026, 11, 4)
    pet = Pet("Luna", "dog")
    pet.add_task(Task("Morning walk", "08:00", duration_mins=30, due_date=day))
    owner = Owner("Sam")
    owner.add_pet(pet)
    meds = Task("Meds", "08:30", duration_mins=10, due_date=day)
    assert Scheduler(owner).check_conflicts(meds) == ""


def test_same_clock_time_on_another_day_does_not_conflict():
    """The same hours on two different dates are two separate visits."""
    pet = Pet("Luna", "dog")
    pet.add_task(Task("Walk", "08:00", duration_mins=30, due_date=date(2026, 11, 4)))
    owner = Owner("Sam")
    owner.add_pet(pet)
    next_day = Task("Walk", "08:00", duration_mins=30, due_date=date(2026, 11, 5))
    assert Scheduler(owner).check_conflicts(next_day) == ""


def test_overlap_across_two_pets_warns_once():
    """One owner cannot start two pets' tasks in the same minutes."""
    day = date(2026, 11, 4)
    luna = Pet("Luna", "dog")
    milo = Pet("Milo", "cat")
    luna.add_task(Task("Morning walk", "08:00", duration_mins=30, due_date=day))
    milo.add_task(Task("Brush fur", "08:10", duration_mins=15, due_date=day))
    owner = Owner("Sam")
    owner.add_pet(luna)
    owner.add_pet(milo)
    warnings = Scheduler(owner).conflict_warnings()
    assert len(warnings) == 1
    assert "Morning walk" in warnings[0]
    assert "Brush fur" in warnings[0]


def test_filter_by_pet_and_by_status():
    """Filters keep one pet's tasks, or only the open or completed ones."""
    luna = Pet("Luna", "dog")
    milo = Pet("Milo", "cat")
    luna.add_task(Task("Walk", "08:00"))
    walk = Task("Brush fur", "09:30")
    milo.add_task(walk)
    milo.add_task(Task("Dinner", "18:00"))
    walk.mark_complete()
    owner = Owner("Sam")
    owner.add_pet(luna)
    owner.add_pet(milo)
    scheduler = Scheduler(owner)
    assert [task.description for task in scheduler.filter_by_pet("milo")] == [
        "Brush fur",
        "Dinner",
    ]
    assert [task.description for task in scheduler.filter_by_status(True)] == ["Brush fur"]
    assert len(scheduler.filter_by_status(False)) == 2


def test_task_outside_available_hours_is_left_off_the_plan():
    """A stored task that starts after the owner's window is not scheduled."""
    day = date(2026, 11, 4)
    pet = Pet("Milo", "cat")
    pet.add_task(Task("Brush fur", "09:30", due_date=day))
    pet.add_task(Task("Late-night check", "23:00", due_date=day))
    owner = Owner("Sam", available_from="07:00", available_until="21:00")
    owner.add_pet(pet)
    plan = Scheduler(owner).todays_schedule(day)
    assert [task.description for _, task in plan] == ["Brush fur"]
