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

My scheduler considers time budget (`available_minutes`), start time, task priority (high/medium/low), and duration. Tasks are sorted by priority first, then shortest duration as a tiebreaker, and time-boxed until the budget runs out — anything that doesn't fit is skipped and explained.

Priority and time budget mattered most since they map to real stakes — a high-priority task like meds shouldn't lose its slot to a lower-priority one just because it was added first. Duration as a tiebreaker keeps the schedule efficient. Owner "preferences" exist as a data field but aren't factored into scheduling yet — a reasonable next step, not essential for v1.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
**2b. Tradeoffs**

My original `detect_conflicts()` warned on every pairwise match (`itertools.combinations`) — clear, but O(k²) and repetitive with 3+ clashing tasks. I simplified it to group tasks by time first (O(k)), emitting one combined warning per clashing slot (e.g., "Conflict at 08:00: 'Morning walk' and 'Meds'"), trading exact wording match to my original spec for better efficiency and readability. Separately, conflict detection only checks exact time matches, not overlapping durations — so a 30-minute task at 08:00 and one starting at 08:15 wouldn't be flagged despite overlapping. I left this as a known limitation to keep detection simple for this phase.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI across the full workflow: brainstorming class design and generating a UML diagram in Phase 1, scaffolding and implementing the class logic in Phases 2–3, writing algorithms (sorting, filtering, recurrence, conflict detection) in Phase 4, generating and reviewing tests in Phase 5, and polishing the UI/README/UML in Phase 6. The most helpful prompts were ones that attached actual files for context (pawpal_system.py, app.py) rather than describing the code abstractly, and ones that asked for review/critique of existing code rather than open-ended generation — e.g. "what edge cases am I missing?" or "how could this be simplified?" surfaced real gaps I wouldn't have found on my own.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
One moment I didn't accept a suggestion as-is: when simplifying detect_conflicts(), I was given a choice between preserving my original wording (less efficient, O(k²)) and a cleaner O(k) version that changed the message format. I chose the more efficient version deliberately, accepting the wording tradeoff rather than keeping the original by default. I verified AI suggestions by running python -m pytest after every change and checking actual terminal output (main.py) rather than trusting the code looked right — several bugs (like the schedule only showing one pet) only surfaced by actually running the app and clicking through the UI myself.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested core model behaviors (task completion, adding/editing/removing tasks), scheduling algorithms (sorting by priority/duration/time, time-budget-aware plan generation, filtering), recurring task logic (daily and weekly occurrence creation, "once" tasks creating nothing), conflict detection (same-time conflicts within and across pets), and edge cases (pets with zero tasks, all-untimed sorting, empty-list handling). These mattered because a scheduling app fails silently in ways that are easy to miss by eye — an off-by-one in recurrence, or a crash on an empty pet, wouldn't show up unless explicitly tested.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I'm fairly confident (4/5) the scheduler works correctly — all 20 automated tests pass, and manual testing through the Streamlit UI confirmed the same behaviors end-to-end. The star held back reflects known simplifications: conflict detection only checks exact time matches, not overlapping durations, so a 30-minute task at 08:00 and one starting at 08:15 wouldn't be flagged despite overlapping. With more time, I'd test that duration-overlap case directly, plus boundary conditions like a task whose duration exactly equals the remaining time budget.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm most satisfied with the scheduling and conflict-detection logic — it handles real edge cases (zero tasks, untimed tasks, multi-pet conflicts) cleanly and explains its reasoning in plain language, which was the actual point of the project: not just a list of tasks, but a system that tells the owner why the plan looks the way it does.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I did another iteration, I'd upgrade conflict detection to check overlapping durations instead of just exact time matches, and actually factor preferences (preferred/avoid times) into generate_plan() instead of leaving it as an unused field.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The biggest lesson was that my value as "lead architect" wasn't writing code — it was making judgment calls the AI couldn't: which tradeoffs were acceptable, which edge cases actually mattered for a pet owner, and when to stop refining and ship a working version