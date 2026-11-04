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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The plan is built by `Scheduler`. Clock time is the order. Priority is shown and mentioned in the "Why" line, and it does not jump a later task ahead of an earlier one.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time` | Sorts with a lambda key that splits each `"HH:MM"` string into integers, so `08:00` comes before `18:00`. `todays_schedule` uses that order. |
| Filtering | `filter_by_pet`, `filter_by_status`, `within_available_hours` | Filter by pet name (ignoring case) or by completed vs open. A task that starts outside `Owner.available_from`–`available_until` stays stored but is left off today's plan. |
| Conflict handling | `check_conflicts`, `conflict_warnings` | Two open tasks conflict when they fall on the same date and their `[start, start + duration)` ranges overlap. The methods return a warning string and leave the times unchanged. If one task ends at the minute the next one starts, that is not a conflict. |
| Recurring tasks | `Task.next_occurrence`, `Scheduler.complete_task` | On completion, a daily task gets a new instance `timedelta(days=1)` later and a weekly task gets one `timedelta(days=7)` later, same clock time, same pet. A `once` task does not repeat. Completing a task that is already done does not add another copy. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
