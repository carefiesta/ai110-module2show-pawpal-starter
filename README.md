# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Output of `python main.py` on 2026-11-04. Tasks were added out of clock order (dinner first). The printed plan is sorted by start time. The 23:00 task is stored but left off the plan because it starts after Alex's available window. Completing the morning walk creates the next day's instance.

```
Today's Schedule for Alex (2026-11-04)
Owner note: Keep evening tasks short.
Available hours: 07:00-21:00

08:00  Luna (dog) — Morning walk (30 min, high priority, daily)
    Why: Earliest open task, so it is scheduled first. Marked high priority, but the clock time still decides the order. Repeats daily.
08:15  Luna (dog) — Meds (10 min, high priority, daily)
    Why: Placed after earlier tasks so care stays in clock order. Marked high priority, but the clock time still decides the order. Repeats daily.
09:30  Milo (cat) — Brush fur (20 min, medium priority, weekly)
    Why: Placed after earlier tasks so care stays in clock order. Repeats weekly.
18:00  Luna (dog) — Dinner (15 min, high priority, daily)
    Why: Placed after earlier tasks so care stays in clock order. Marked high priority, but the clock time still decides the order. Repeats daily.

Conflicts:
  Warning: 'Morning walk' (Luna, 08:00-08:30) overlaps 'Meds' (Luna, 08:15-08:25).

filter_by_pet('Milo'): 09:30 Brush fur, 23:00 Late-night check
filter_by_status(open): 5 task(s)

Completed 'Morning walk' on 2026-11-04.
Next instance: 2026-11-05 at 08:00 (daily).
```

## 🧪 Testing PawPal+

The suite lives in `tests/test_pawpal.py`. It covers marking a task complete, counting tasks on a pet and across an owner, sort order (including that the pet's own list is not rearranged), the daily plan skipping other dates, daily and weekly recurrence, a `once` task not repeating, a second completion not adding an extra copy, overlap warnings, back-to-back tasks that should not warn, the same clock time on a different day, an overlap between two pets reported once, filtering by pet and by status, and leaving an after-hours task off the plan.

`pytest-cov` is not installed, so there is no coverage percentage here. The description above is the set of behaviors the tests actually exercise.

**Confidence level: ★★★★☆ (4/5).** The rules above pass. A bad clock string such as `8pm` and a task that runs past midnight are not in this suite. The Streamlit page was also clicked through: add two pets, add tasks, an overlap warning, mark complete (next daily instance), a blank pet name, and a later-added earlier task sorting above a later one.

Command:

```bash
python -m pytest -v
```

Output from that command:

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- /tmp/pawpal-venv/bin/python
cachedir: .pytest_cache
rootdir: /workspace
plugins: anyio-4.16.0
collecting ... collected 15 items

tests/test_pawpal.py::test_mark_complete_sets_flag PASSED                [  6%]
tests/test_pawpal.py::test_add_task_increases_count PASSED               [ 13%]
tests/test_pawpal.py::test_owner_all_tasks_counts_every_pet PASSED       [ 20%]
tests/test_pawpal.py::test_sort_by_time_orders_earliest_first PASSED     [ 26%]
tests/test_pawpal.py::test_todays_schedule_is_sorted_and_skips_other_days PASSED [ 33%]
tests/test_pawpal.py::test_daily_task_spawns_the_next_day PASSED         [ 40%]
tests/test_pawpal.py::test_weekly_task_spawns_seven_days_later PASSED    [ 46%]
tests/test_pawpal.py::test_once_task_does_not_repeat PASSED              [ 53%]
tests/test_pawpal.py::test_completing_twice_does_not_add_another_copy PASSED [ 60%]
tests/test_pawpal.py::test_overlap_returns_a_warning PASSED              [ 66%]
tests/test_pawpal.py::test_back_to_back_tasks_do_not_conflict PASSED     [ 73%]
tests/test_pawpal.py::test_same_clock_time_on_another_day_does_not_conflict PASSED [ 80%]
tests/test_pawpal.py::test_overlap_across_two_pets_warns_once PASSED     [ 86%]
tests/test_pawpal.py::test_filter_by_pet_and_by_status PASSED            [ 93%]
tests/test_pawpal.py::test_task_outside_available_hours_is_left_off_the_plan PASSED [100%]

============================== 15 passed in 0.01s ==============================
```

## 📐 Smarter Scheduling

The plan is built by `Scheduler`. Clock time is the order. Priority is shown and mentioned in the "Why" line, and it does not jump a later task ahead of an earlier one.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time` | Sorts with a lambda key that splits each `"HH:MM"` string into integers, so `08:00` comes before `18:00`. `todays_schedule` uses that order. |
| Filtering | `filter_by_pet`, `filter_by_status`, `within_available_hours` | Filter by pet name (ignoring case) or by completed vs open. A task that starts outside `Owner.available_from`–`available_until` stays stored but is left off today's plan. |
| Conflict handling | `check_conflicts`, `conflict_warnings` | Two open tasks conflict when they fall on the same date and their `[start, start + duration)` ranges overlap. The methods return a warning string and leave the times unchanged. If one task ends at the minute the next one starts, that is not a conflict. `conflict_warnings(on)` limits the list to one date, which is what the Streamlit page shows. |
| Recurring tasks | `Task.next_occurrence`, `Scheduler.complete_task` | On completion, a daily task gets a new instance `timedelta(days=1)` later and a weekly task gets one `timedelta(days=7)` later, same clock time, same pet. A `once` task does not repeat. Completing a task that is already done does not add another copy. |

## Features

- Track one owner and any number of pets, each with its own care tasks
- Add a pet (name, species, age) and add a task (clock time, duration, priority, frequency, due date)
- Build a daily plan sorted by start time, with a short reason on each row
- Leave out tasks that start outside the owner's available hours, and filter by pet or by completed status in the scheduler
- Warn when two open tasks on the same date overlap, without moving either one
- On completion, create the next daily or weekly instance with `timedelta`
- Keep the household in `st.session_state` so the Streamlit page and `main.py` share one model

## 📸 Demo Walkthrough

1. In the project folder, install dependencies with `pip install -r requirements.txt`, then start the page with `streamlit run app.py`. The command-line version of the same scheduler is `python main.py`. Its printout is the Sample Output section above.
2. Set **Owner name**. The note field is optional. Text typed there is shown above the plan and is not used to reorder tasks. Set **Available from** and **Available until**. If the start is later than the end, the page warns that the plan will be empty.
3. Under **Add a pet**, enter a name, choose a species, set the age, and press **Add pet**. A success message names the pet. Add a second pet the same way. A blank name shows a warning and does not add a pet.
4. Under **Schedule a task**, choose the pet and enter a description, **Time**, **Duration (minutes)**, **Priority**, **Frequency** (`once`, `daily`, or `weekly`), and **Due date**. Press **Add task**. Add another task at a different time. Enter the later clock time first if you want to see that the table does not follow click order.
5. Under **Daily plan**, set **Plan date** to that due date. The table is ordered by start time. The Why column says the earliest open task is scheduled first, and that a high priority does not move a later task ahead of an earlier one. **All tasks** lists every task, including completed ones and ones on other dates.
6. Add a task that starts while another task that day is still going. For example, a morning walk at 08:00 for 30 minutes and meds at 08:15 for 10 minutes. The page shows a warning that names both tasks. The new task is still saved. When that date has open tasks and none of them overlap, the page shows a success message: "No scheduling conflicts."
7. Press **Mark complete** on a daily task. The success message names the next date, one day later, at the same time. A weekly task's next instance is seven days later. A `once` task does not add a row. The finished row stays under **All tasks** with status `done`, and the new instance is `open`.
8. Move **Available until** to a time earlier than some task's start. That task drops out of the plan table and appears under the caption "Open on this date, outside the available hours," where it can still be marked complete. It also stays in **All tasks**.

**Screenshot or video** *(optional)*: not included. The steps above, together with the `python main.py` output, are the demo.
