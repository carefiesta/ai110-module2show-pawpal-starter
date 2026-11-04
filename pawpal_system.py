"""PawPal+ domain model.

Task, Pet, and Owner store the household. Scheduler orders the day,
filters tasks, repeats daily and weekly care, and warns about overlaps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


def minutes_from_clock(clock: str) -> int:
    """Convert an 'HH:MM' string to minutes after midnight."""
    hours, mins = clock.split(":")
    return int(hours) * 60 + int(mins)


def clock_from_minutes(total: int) -> str:
    """Convert minutes after midnight back to 'HH:MM'."""
    return f"{total // 60:02d}:{total % 60:02d}"


@dataclass
class Task:
    """One pet-care activity, such as a walk or a meal."""

    description: str
    time: str
    frequency: str = "once"
    completed: bool = False
    duration_mins: int = 30
    priority: str = "medium"
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def end_minutes(self) -> int:
        """Return the minute-of-day when this task finishes."""
        return minutes_from_clock(self.time) + self.duration_mins

    def overlaps(self, other: Task) -> bool:
        """Return True when two tasks on the same day share any minute."""
        if self.due_date != other.due_date:
            return False
        start = minutes_from_clock(self.time)
        other_start = minutes_from_clock(other.time)
        return start < other.end_minutes() and other_start < self.end_minutes()

    def next_occurrence(self) -> Task | None:
        """Build the next daily or weekly copy, leaving this task unchanged."""
        freq = self.frequency.lower()
        if freq == "daily":
            step = timedelta(days=1)
        elif freq == "weekly":
            step = timedelta(days=7)
        else:
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            completed=False,
            duration_mins=self.duration_mins,
            priority=self.priority,
            due_date=self.due_date + step,
        )


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """The person responsible for one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_from: str = "00:00"
    available_until: str = "23:59"
    preferences: str = ""

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs for every task this owner tracks."""
        pairs = []
        for pet in self.pets:
            for task in pet.tasks:
                pairs.append((pet, task))
        return pairs


class Scheduler:
    """Plans an owner's care tasks: order, filters, repeats, and overlaps."""

    def __init__(self, owner: Owner) -> None:
        """Store the owner whose tasks this scheduler will plan."""
        self.owner = owner

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return a new list of tasks ordered by HH:MM start time."""
        return sorted(tasks, key=lambda task: tuple(int(part) for part in task.time.split(":")))

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return tasks that belong to the pet with this name."""
        found = []
        for pet, task in self.owner.all_tasks():
            if pet.name.lower() == pet_name.lower():
                found.append(task)
        return found

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return tasks that are completed, or tasks that are still open."""
        return [task for _, task in self.owner.all_tasks() if task.completed is completed]

    def within_available_hours(self, task: Task) -> bool:
        """Return True if the task starts inside the owner's available window."""
        start = minutes_from_clock(task.time)
        open_at = minutes_from_clock(self.owner.available_from)
        close_at = minutes_from_clock(self.owner.available_until)
        return open_at <= start <= close_at

    def check_conflicts(self, new_task: Task) -> str:
        """Return a warning if new_task overlaps an open task, else ''."""
        messages = []
        for pet, task in self.owner.all_tasks():
            if task is new_task or task.completed:
                continue
            if new_task.overlaps(task):
                messages.append(
                    "Warning: "
                    f"'{new_task.description}' ({new_task.time}-"
                    f"{clock_from_minutes(new_task.end_minutes())}) overlaps "
                    f"'{task.description}' for {pet.name} "
                    f"({task.time}-{clock_from_minutes(task.end_minutes())})."
                )
        return " ".join(messages)

    def conflict_warnings(self) -> list[str]:
        """Return one warning for each overlapping pair of open tasks."""
        open_pairs = [(pet, task) for pet, task in self.owner.all_tasks() if not task.completed]
        warnings = []
        for index, (pet_a, task_a) in enumerate(open_pairs):
            for pet_b, task_b in open_pairs[index + 1 :]:
                if task_a.overlaps(task_b):
                    warnings.append(
                        "Warning: "
                        f"'{task_a.description}' ({pet_a.name}, {task_a.time}-"
                        f"{clock_from_minutes(task_a.end_minutes())}) overlaps "
                        f"'{task_b.description}' ({pet_b.name}, {task_b.time}-"
                        f"{clock_from_minutes(task_b.end_minutes())})."
                    )
        return warnings

    def complete_task(self, pet: Pet, task: Task) -> Task | None:
        """Mark a task complete and append the next repeat when it has one."""
        if task.completed:
            return None
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            pet.add_task(upcoming)
        return upcoming

    def todays_schedule(self, on: date | None = None) -> list[tuple[Pet, Task]]:
        """Return today's open, in-window tasks, earliest start first."""
        day = date.today() if on is None else on
        chosen = []
        for pet, task in self.owner.all_tasks():
            if task.completed or task.due_date != day:
                continue
            if not self.within_available_hours(task):
                continue
            chosen.append((pet, task))
        ordered = self.sort_by_time([task for _, task in chosen])
        pet_for = {id(task): pet for pet, task in chosen}
        return [(pet_for[id(task)], task) for task in ordered]

    def explain(self, task: Task, position: int) -> str:
        """Give a short reason for this task's place in the plan."""
        if position == 0:
            reason = "Earliest open task, so it is scheduled first."
        else:
            reason = "Placed after earlier tasks so care stays in clock order."
        if task.priority == "high":
            reason += " Marked high priority, but the clock time still decides the order."
        frequency = task.frequency.lower()
        if frequency == "daily":
            reason += " Repeats daily."
        elif frequency == "weekly":
            reason += " Repeats weekly."
        return reason
