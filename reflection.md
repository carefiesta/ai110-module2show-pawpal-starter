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

No change yet. The file is still the skeleton from the draft diagram. I will update this section if implementation forces a change.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
