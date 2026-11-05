"""Streamlit front end for PawPal+.

One Owner lives in st.session_state. Adding a pet, adding a task, and
marking a task complete all call the classes in pawpal_system.py.
"""

from datetime import date, time as clock_time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")


def clock_text(value: clock_time) -> str:
    """Format a time widget value as HH:MM."""
    return value.strftime("%H:%M")


def text_to_clock(value: str) -> clock_time:
    """Parse an HH:MM string into a time for the widgets."""
    hours, mins = value.split(":")
    return clock_time(int(hours), int(mins))


def offer_complete(scheduler: Scheduler, pet: Pet, task: Task) -> None:
    """Show a button that marks one task complete and stores the next repeat."""
    label = (
        f"Mark complete: {pet.name} — {task.description} "
        f"({task.due_date.isoformat()} {task.time})"
    )
    if st.button(label, key=f"done-{id(task)}"):
        upcoming = scheduler.complete_task(pet, task)
        if upcoming is None:
            st.session_state.notice = f"Completed '{task.description}'."
        else:
            st.session_state.notice = (
                f"Completed '{task.description}'. "
                f"Next instance: {upcoming.due_date.isoformat()} at {upcoming.time} ({upcoming.frequency})."
            )
        st.rerun()


st.title("🐾 PawPal+")
st.markdown(
    "Plan care for every pet in the household. "
    "The page keeps one Owner in session state and uses the same classes as `main.py`."
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
if "pet_form_id" not in st.session_state:
    st.session_state.pet_form_id = 0
if "task_form_id" not in st.session_state:
    st.session_state.task_form_id = 0

notice = st.session_state.pop("notice", "")
notice_warning = st.session_state.pop("notice_warning", "")
if notice:
    st.success(notice)
if notice_warning:
    st.warning(notice_warning)

owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.preferences = st.text_input(
    "Note (shown on the plan, not used to reorder tasks)",
    value=owner.preferences,
)
hour_left, hour_right = st.columns(2)
with hour_left:
    available_from = st.time_input(
        "Available from",
        value=text_to_clock(owner.available_from),
        step=60,
    )
with hour_right:
    available_until = st.time_input(
        "Available until",
        value=text_to_clock(owner.available_until),
        step=60,
    )
owner.available_from = clock_text(available_from)
owner.available_until = clock_text(available_until)
if owner.available_from > owner.available_until:
    st.warning("Available from is later than available until, so the plan will be empty.")

st.subheader("Add a pet")
with st.form(f"add_pet_{st.session_state.pet_form_id}"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1, step=1)
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    cleaned_name = pet_name.strip()
    if cleaned_name:
        owner.add_pet(Pet(cleaned_name, species, int(age)))
        st.session_state.notice = f"Added {cleaned_name}."
        st.session_state.pet_form_id += 1
        st.rerun()
    else:
        st.warning("Enter a pet name first.")

if owner.pets:
    pet_bits = [f"{pet.name} ({pet.species}, age {pet.age})" for pet in owner.pets]
    st.markdown("**Pets:** " + ", ".join(pet_bits))
else:
    st.info("No pets yet. Add one above.")

st.subheader("Schedule a task")
if not owner.pets:
    st.caption("Add a pet before scheduling a task.")
else:
    with st.form(f"add_task_{st.session_state.task_form_id}"):
        pet_index = st.selectbox(
            "Pet",
            options=list(range(len(owner.pets))),
            format_func=lambda index: owner.pets[index].name,
        )
        description = st.text_input("Task", placeholder="Morning walk")
        task_time = st.time_input("Time", value=clock_time(8, 0), step=60)
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30, step=5)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        due = st.date_input("Due date", value=date.today())
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        cleaned_description = description.strip()
        if not cleaned_description:
            st.warning("Enter a task description.")
        else:
            task = Task(
                cleaned_description,
                clock_text(task_time),
                frequency,
                duration_mins=int(duration),
                priority=priority,
                due_date=due,
            )
            warning = scheduler.check_conflicts(task)
            owner.pets[pet_index].add_task(task)
            if warning:
                st.session_state.notice_warning = warning + " The task was still added."
            else:
                st.session_state.notice = (
                    f"Added '{task.description}' for {owner.pets[pet_index].name} at {task.time}."
                )
            st.session_state.task_form_id += 1
            st.rerun()

st.subheader("Daily plan")
st.caption("Sorted by start time. A high priority does not jump ahead of an earlier task.")
plan_day = st.date_input("Plan date", value=date.today())
if owner.preferences:
    st.markdown(f"**Owner note:** {owner.preferences}")
st.markdown(f"Available hours: {owner.available_from}–{owner.available_until}")

plan = scheduler.todays_schedule(plan_day)
if not plan:
    st.info("No open tasks inside the available hours for this date.")
else:
    rows = []
    for index, (pet, task) in enumerate(plan):
        rows.append(
            {
                "Time": task.time,
                "Pet": pet.name,
                "Task": task.description,
                "Duration": f"{task.duration_mins} min",
                "Priority": task.priority,
                "Frequency": task.frequency,
                "Why": scheduler.explain(task, index),
            }
        )
    st.table(rows)
    for pet, task in plan:
        offer_complete(scheduler, pet, task)

shown_ids = {id(task) for _, task in plan}
left_off = [
    (pet, task)
    for pet, task in owner.all_tasks()
    if task.due_date == plan_day and not task.completed and id(task) not in shown_ids
]
if left_off:
    st.caption("Open on this date, outside the available hours:")
    for pet, task in left_off:
        offer_complete(scheduler, pet, task)

warnings = scheduler.conflict_warnings(plan_day)
open_on_day = [
    task
    for _, task in owner.all_tasks()
    if not task.completed and task.due_date == plan_day
]
if warnings:
    for warning in warnings:
        st.warning(warning)
elif open_on_day:
    st.success("No scheduling conflicts.")

st.subheader("All tasks")
if not owner.all_tasks():
    st.caption("No tasks yet.")
else:
    all_rows = []
    for pet, task in owner.all_tasks():
        all_rows.append(
            {
                "Due": task.due_date.isoformat(),
                "Time": task.time,
                "Pet": pet.name,
                "Task": task.description,
                "Duration": f"{task.duration_mins} min",
                "Priority": task.priority,
                "Frequency": task.frequency,
                "Status": "done" if task.completed else "open",
            }
        )
    st.table(all_rows)
