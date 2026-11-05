# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I drew four classes in `diagrams/uml_draft.mmd` before writing any method logic. The skeleton in `pawpal_system.py` follows that diagram.

- **Task** is one care activity. It stores a description, a clock time (`HH:MM`), a frequency (`once`, `daily`, or `weekly`), and a completed flag. `mark_complete()` is the only behavior on the task itself.
- **Pet** stores the name, species, and age, plus the list of tasks for that animal. `add_task()` adds to the list. Tasks live on the pet so a walk for one dog is not mixed up with another pet's meds.
- **Owner** stores the person's name and the pets they care for. `add_pet()` registers a pet. `all_tasks()` gathers every task, because the daily plan is for the household, not for a single animal.
- **Scheduler** receives an owner and is responsible for the daily plan. It does not keep a second copy of the tasks.

Relationships: one owner cares for many pets, one pet has many tasks, and the scheduler reads the owner.

**b. Design changes**

Yes. The draft task only stored a description, a clock time, a frequency, and a completed flag. That was enough to list a day, and it was not enough to schedule one.

- `duration_mins` was added so a conflict is a span of time. Two tasks that start at different minutes can still overlap.
- `due_date` was added so a repeat can be a new task on a later calendar day. `timedelta` needs a date, not only `"HH:MM"`.
- `priority` was added because the scenario asks for it. It is stored and explained. It does not reorder the plan.
- `Owner.available_from`, `available_until`, and `preferences` were added so the household has a time window and a note. The note is printed. The scheduler does not try to read the sentence and guess a rule from it.

`Scheduler` gained `sort_by_time`, `filter_by_pet`, `filter_by_status`, `check_conflicts`, and `complete_task`. `Task.mark_complete()` still only flips the flag. The scheduler is what appends the next occurrence to the pet. That kept the original "mark complete" behavior and put the planning rules in one place.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at four things:

- **Clock time.** `sort_by_time` orders open tasks by the `"HH:MM"` start. This is the constraint that decides the plan.
- **Available hours.** `within_available_hours` drops a task from today's plan when its start is outside `Owner.available_from` and `available_until`. The task is still stored. In the CLI demo, Milo's 23:00 check is kept by `filter_by_pet` and left off the 07:00–21:00 plan.
- **Overlaps.** `check_conflicts` compares `[start, start + duration)` on the same `due_date` across every pet, because one person cannot do two care tasks at once.
- **Priority and the free-text preference.** Priority is saved on the task and mentioned in `explain`. The preference string is saved on the owner and printed. Neither one moves a task.

Time mattered most because walks, meals, and medication are tied to a clock. If a high-priority dinner sorted ahead of breakfast, the pet would be fed at the wrong time. Priority is a label for the owner, not a reason to ignore the clock.

**b. Tradeoffs**

The scheduler warns about an overlap and leaves both tasks at the times that were entered. It does not search for an empty slot or slide one task later. That is reasonable here: a dose or a meal often cannot move by an hour, and a silent change would hide the clash. The warning (see `conflict_warnings`) is the signal, and the owner decides what to move.

A second, related choice: a high-priority task that starts later stays later. `sort_by_time` does not break ties with priority. The time on the task is treated as a commitment. Priority is still visible so the owner can see which of two overlapping tasks they care about more.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant for the class diagram, the skeletons in `pawpal_system.py`, and a first pass at the scheduling methods and the pytest file. I checked the result by reading `Scheduler`, running `python main.py`, and running `python -m pytest`. The rule that an overlap only warns, and does not move a task, is the one in `check_conflicts`.

Breaking the project into small steps worked best. I followed the CodePath order: first the class diagram and empty classes, then the main classes and a demo script, then the Streamlit page, then sorting and conflict checks, then tests, and finally the README. When I asked for one step at a time, I could run it and see whether it worked before moving on. Asking for everything at once would have been too much for me to check.

**b. Judgment and verification**

The scheduler could have moved a task to a free time slot whenever two tasks overlapped. I decided it should only show a warning and leave both times alone, because a pet's medicine or meal time usually can't just move. I checked this by running `python main.py` to see the warning, and `python -m pytest` to make sure all 15 tests passed.

---

## 4. Testing and Verification

**a. What you tested**

`tests/test_pawpal.py` checks the behaviors that would silently build a wrong day:

- `mark_complete` flips the flag, and adding a task increases the count, including across two pets.
- `sort_by_time` orders 18:00, 08:00, 12:30 as walk, meds, dinner, and does not rewrite the pet's list. `todays_schedule` uses that order and drops a task whose `due_date` is a different day.
- A daily completion creates the next calendar day. A weekly completion creates a task seven days later and keeps duration and priority. A `once` task does not repeat. Completing a daily task a second time does not add a third copy.
- An overlap returns a warning string. A task that starts at the previous task's end minute does not. The same clock time on another date does not. Two pets overlapping produce one warning, not two.
- `filter_by_pet` matches a name without caring about case. `filter_by_status` splits open and done. A task after `available_until` stays stored and is left off the plan.

These matter because a sort that follows insertion order, a repeat that forgets the date, or a conflict check that only compares start times would all look fine in a short demo and still be wrong.

**b. Confidence**

4 out of 5. The cases above pass under `python -m pytest -v` (15 passed). The Streamlit page was also clicked through: two pets, several tasks, an overlap warning, marking a daily walk complete (the next instance is the next day), a blank pet name rejected, and a later-added 08:00 task sorting above an 08:15 task. Next checks would be a clock string that is not `HH:MM` and a duration that crosses midnight.

---

## 5. Reflection

**a. What went well**

The split between the household (`Owner`, `Pet`, `Task`) and the planning rules on `Scheduler` is the part that stayed easy to test. Sort order, repeats, and overlaps are locked in `tests/test_pawpal.py`, and the Streamlit page calls those same methods instead of keeping a second list of dicts.

I'm happy that the app actually works the way the instructions described. Tasks show up in time order, a daily or weekly task comes back after I mark it done, and the app warns me when two tasks overlap. Seeing all the tests pass gave me confidence that it wasn't just working by luck.

**b. What you would improve**

I would save the household to a file and load it when the app starts. `st.session_state` keeps the owner for the browser session only. I would also make `sort_by_time` reject a string that is not `HH:MM` instead of raising. The page avoids that with a time picker, and `main.py` only uses valid times.

**c. Key takeaway**

Planning the design first really mattered. My first diagram was simpler than the final one: I had to add a due date and a duration once I realized repeating tasks and overlap checks needed that information. My AI assistant was helpful for writing code, but I still had to decide how things should work and check the results myself, so I stayed in charge of the design.
