"""PawPal+ domain model.

The classes match the UML draft: Task, Pet, Owner, and Scheduler.
Method bodies are filled in after this skeleton.
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
        pass


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass


@dataclass
class Owner:
    """The person responsible for one or more pets."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        pass

    def all_tasks(self) -> list:
        """Return every task across all of this owner's pets."""
        pass


class Scheduler:
    """Builds a daily care plan from an owner's pets and tasks."""

    def __init__(self, owner: Owner) -> None:
        """Store the owner whose tasks this scheduler will plan."""
        self.owner = owner

    def todays_schedule(self) -> list:
        """Return the tasks planned for today."""
        pass
