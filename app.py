"""Streamlit front end for PawPal+.

The page keeps one Owner in st.session_state and calls the classes in
pawpal_system.py. Refreshing the script does not wipe the household.
"""

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown(
    "Plan care tasks for every pet in the household. "
    "This page uses the same Owner, Pet, Task, and Scheduler classes as the CLI."
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner
scheduler = Scheduler(owner)

owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1, step=1)
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    cleaned_name = pet_name.strip()
    if cleaned_name:
        owner.add_pet(Pet(cleaned_name, species, int(age)))
        st.success(f"Added {cleaned_name}.")
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
    with st.form("add_task", clear_on_submit=True):
        pet_index = st.selectbox(
            "Pet",
            options=list(range(len(owner.pets))),
            format_func=lambda index: owner.pets[index].name,
        )
        description = st.text_input("Task", placeholder="Morning walk")
        clock = st.text_input("Time (HH:MM)", value="08:00")
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        cleaned_description = description.strip()
        if not cleaned_description:
            st.warning("Enter a task description.")
        else:
            task = Task(cleaned_description, clock.strip(), frequency)
            owner.pets[pet_index].add_task(task)
            st.success(f"Added '{task.description}' for {owner.pets[pet_index].name}.")

st.subheader("Today's schedule")
plan = scheduler.todays_schedule()
if not plan:
    st.info("No open tasks yet.")
else:
    rows = []
    for pet, task in plan:
        rows.append(
            {
                "Time": task.time,
                "Pet": pet.name,
                "Task": task.description,
                "Frequency": task.frequency,
                "Status": "done" if task.completed else "open",
            }
        )
    st.table(rows)
