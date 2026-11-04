"""PawPal+ domain model.

Task, Pet, and Owner store the household. Scheduler builds the daily plan.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    """One pet-care activity, such as a walk or a meal."""

    description: str
    time: str
    frequency: str = "once"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """The person responsible for one or more pets."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list:
        """Return (pet, task) pairs for every task this owner tracks."""
        pairs = []
        for pet in self.pets:
            for task in pet.tasks:
                pairs.append((pet, task))
        return pairs


class Scheduler:
    """Builds a daily care plan from an owner's pets and tasks."""

    def __init__(self, owner: Owner) -> None:
        """Store the owner whose tasks this scheduler will plan."""
        self.owner = owner

    def todays_schedule(self) -> list:
        """Return open tasks in the order they were added."""
        planned = []
        for pet, task in self.owner.all_tasks():
            if not task.completed:
                planned.append((pet, task))
        return planned
