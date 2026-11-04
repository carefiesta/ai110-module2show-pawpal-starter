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

> TODO (David): say which kinds of prompts or assistant features helped you most. Factual hint: the repo was built in phases (diagram and skeletons, core classes and `main.py`, Streamlit session state, sorting and conflicts, pytest, then the README and `diagrams/uml_final.mmd`). A request that stayed inside one phase was easier to check than a request for the whole app.

**b. Judgment and verification**

> TODO (David): describe one suggestion you did not take as-is, and how you checked the version you kept. Factual hint: `check_conflicts` returns a warning and leaves both times unchanged. `mark_complete` only sets `completed`. The next date comes from `Task.next_occurrence` (`timedelta` of 1 day or 7 days) and `complete_task` appends that new task to the pet. Say what you compared that with, and that you used pytest plus `python main.py` to check it.

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

> TODO (David): change this confidence note if your own manual checks made you more or less sure.

---

## 5. Reflection

**a. What went well**

The split between the household (`Owner`, `Pet`, `Task`) and the planning rules on `Scheduler` is the part that stayed easy to test. Sort order, repeats, and overlaps are locked in `tests/test_pawpal.py`, and the Streamlit page calls those same methods instead of keeping a second list of dicts.

> TODO (David): add what you were most satisfied with in your own words.

**b. What you would improve**

I would save the household to a file and load it when the app starts. `st.session_state` keeps the owner for the browser session only. I would also make `sort_by_time` reject a string that is not `HH:MM` instead of raising. The page avoids that with a time picker, and `main.py` only uses valid times.

**c. Key takeaway**

> TODO (David): write one thing you learned about designing the system, or about working with an AI assistant while you stayed the lead on the design. Factual hint: `diagrams/uml_draft.mmd` is smaller than `diagrams/uml_final.mmd`. `due_date` and `duration_mins` were added so a repeat and an overlap had data to use, and the final diagram was updated to match the code.
