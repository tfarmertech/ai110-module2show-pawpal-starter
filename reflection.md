# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
1a. Initial design
PawPal+ is built around four classes split between data and behavior.
Owner holds contact info, a daily time budget (available_minutes), preferences, and a list of pets, with methods to manage pets (add_pet, remove_pet, list_pets).
Pet is a dataclass storing a pet's basic info (name, species, breed, age, notes) and its tasks, with methods to manage those tasks (add_task, edit_task, remove_task).
Task is a dataclass describing a single care task (title, duration, priority, recurrence, category, preferred time, completed), with methods to support scheduling (priority_score(), is_due_today()).
Scheduler is the brains of the system: given tasks and constraints (time budget, start time, preferences), it sorts tasks, builds a time-boxed daily plan, and explains the reasoning behind it.
Relationships: an Owner owns many Pets, a Pet has many Tasks, and Scheduler operates on Tasks/Pet without owning them. Keeping data (Pet, Task) separate from behavior (Owner, Scheduler) keeps the scheduling logic isolated and easier to test.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
No changes
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
