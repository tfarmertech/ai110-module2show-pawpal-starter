"""PawPal+ Streamlit UI.

Thin presentation layer wired to the domain logic in pawpal_system.py.
The UI collects input and renders output; all scheduling/CRUD logic lives
in the Owner / Pet / Task / Scheduler classes.
"""

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Sentinel option in the category dropdown that reveals a "new category" input.
NEW_CATEGORY = "➕ Add new category..."

# Common care tasks -> typical defaults. Selecting one pre-fills the add-task
# form, which the user can still tweak before saving.
TASK_TEMPLATES = {
    "Morning walk": {"duration": 30, "category": "walk", "priority": "high", "recurrence": "daily"},
    "Feeding": {"duration": 10, "category": "feeding", "priority": "high", "recurrence": "daily"},
    "Meds": {"duration": 5, "category": "meds", "priority": "high", "recurrence": "daily"},
    "Grooming": {"duration": 45, "category": "grooming", "priority": "low", "recurrence": "weekly"},
    "Play/enrichment": {"duration": 20, "category": "enrichment", "priority": "medium", "recurrence": "daily"},
}
TEMPLATE_PLACEHOLDER = "— Choose a template —"

# Default values for the (reactive) add-task widgets, kept in session_state so
# templates/resets can prefill them before the widgets are instantiated.
_TASK_INPUT_DEFAULTS = {
    "ti_title": "",
    "ti_duration": 20,
    "ti_priority": "medium",
    "ti_recurrence": "daily",
    "ti_preftime": "",
    "ti_template": TEMPLATE_PLACEHOLDER,
}


def set_flash(kind: str, message: str) -> None:
    """Queue a one-shot message to show after the next rerun (st.success, etc.)."""
    st.session_state.flash = (kind, message)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
# Streamlit re-runs this whole script top-to-bottom on every interaction.
# We store the *Owner object itself* in st.session_state (not raw dicts) so the
# entire object graph — Owner -> Pets -> Tasks — survives each rerun with its
# methods intact. That lets the UI call owner.add_pet(), pet.add_task(), etc.
# directly and have the mutations persist.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", email="", available_minutes=90)
if "start_time" not in st.session_state:
    st.session_state.start_time = "08:00"

owner: Owner = st.session_state.owner

# Known task categories persist across reruns. Seed with sensible defaults plus
# any categories already present on existing tasks, so the dropdown "remembers".
if "known_categories" not in st.session_state:
    seed = {"general", "walk", "feeding", "meds", "grooming", "enrichment"}
    for pet in owner.pets:
        for task in pet.tasks:
            seed.add(task.category)
    st.session_state.known_categories = sorted(seed)

# Ensure add-task widget defaults exist before those widgets are created.
for _key, _val in _TASK_INPUT_DEFAULTS.items():
    st.session_state.setdefault(_key, _val)
st.session_state.setdefault("ti_category_choice", "general")

# After adding a task we intentionally KEEP the field values (title, duration,
# priority, recurrence, category) and the selected template, so the same task
# can be applied to another pet without retyping. The only post-add cleanup is
# for the "add new category" flow: once a new category is created, select it and
# hide the free-text input. (Streamlit forbids writing a widget's state after
# it's instantiated, so we do this here — before the widgets are created.)
_select_cat = st.session_state.pop("_select_category_after_add", None)
if _select_cat is not None:
    st.session_state.ti_category_choice = _select_cat
    st.session_state.pop("ti_newcat", None)

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care around the time you have.")

# One-shot flash message (shown once, then cleared so it never lingers).
if "flash" in st.session_state:
    _kind, _msg = st.session_state.pop("flash")
    getattr(st, _kind)(_msg)

# ---------------------------------------------------------------------------
# Owner settings
# ---------------------------------------------------------------------------
with st.expander("Owner & daily budget", expanded=True):
    with st.form("owner_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Owner name", value=owner.name)
            email = st.text_input("Email", value=owner.email)
        with c2:
            available_minutes = st.number_input(
                "Available minutes today",
                min_value=5,
                max_value=1440,
                value=int(owner.available_minutes),
                step=5,
            )
            start_time = st.text_input(
                "Day starts at (HH:MM)", value=st.session_state.start_time
            )
        if st.form_submit_button("Save owner settings"):
            owner.name = name
            owner.email = email
            owner.available_minutes = int(available_minutes)
            st.session_state.start_time = start_time
            set_flash("success", "Owner settings saved!")
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------------
st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    st.markdown("**Add a pet**")
    pc1, pc2 = st.columns(2)
    with pc1:
        pet_name = st.text_input("Name", value="")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    with pc2:
        breed = st.text_input("Breed", value="")
        notes = st.text_area("Notes", value="", height=80)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.warning("Please enter a pet name.")
        else:
            pet = Pet(
                name=pet_name.strip(),
                species=species,
                breed=breed.strip(),
                age=int(age),
                notes=notes.strip(),
            )
            owner.add_pet(pet)  # <-- new-pet submissions are handled here
            set_flash("success", f"Added {pet.name}!")
            st.rerun()

pets = owner.list_pets()
if not pets:
    st.info("No pets yet. Add one above to get started.")
else:
    for pet in pets:
        cols = st.columns([6, 1])
        cols[0].write(
            f"**{pet.name}** — {pet.species}"
            + (f", {pet.breed}" if pet.breed else "")
            + f" • {len(pet.tasks)} task(s)"
        )
        if cols[1].button("Remove", key=f"rmpet_{pet.name}"):
            owner.remove_pet(pet.name)
            set_flash("info", f"Removed {pet.name}.")
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Manage tasks for a selected pet
# ---------------------------------------------------------------------------
st.subheader("Tasks")

if not pets:
    st.info("Add a pet first, then add its care tasks here.")
else:
    pet_names = [p.name for p in pets]
    selected_name = st.selectbox("Choose a pet", pet_names, key="task_pet")
    selected_pet = next(p for p in pets if p.name == selected_name)

    # --- Current tasks table ---
    if selected_pet.tasks:
        st.table(
            [
                {
                    "ID": t.id,
                    "Task": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Recurrence": t.recurrence,
                    "Category": t.category,
                    "Done": "✅" if t.completed else "",
                }
                for t in selected_pet.tasks
            ]
        )
    else:
        st.caption("No tasks for this pet yet.")

    # --- Add a task (reactive widgets so templates + category reveal work) ---
    st.markdown(f"**Add a task for {selected_pet.name}**")

    # Feature 3: task templates. Picking one and clicking "Use template"
    # pre-fills the fields below; the user can still edit anything before saving.
    qt1, qt2 = st.columns([3, 1])
    with qt1:
        st.selectbox(
            "Quick template",
            [TEMPLATE_PLACEHOLDER, *TASK_TEMPLATES.keys()],
            key="ti_template",
        )
    with qt2:
        st.markdown("<div style='height:1.8em'></div>", unsafe_allow_html=True)
        use_template = st.button("Use template")

    if use_template:
        choice = st.session_state.ti_template
        if choice in TASK_TEMPLATES:
            tpl = TASK_TEMPLATES[choice]
            st.session_state.ti_title = choice
            st.session_state.ti_duration = tpl["duration"]
            st.session_state.ti_priority = tpl["priority"]
            st.session_state.ti_recurrence = tpl["recurrence"]
            category = tpl["category"]
            if category not in st.session_state.known_categories:
                st.session_state.known_categories = sorted(
                    set(st.session_state.known_categories) | {category}
                )
            st.session_state.ti_category_choice = category
            st.rerun()
        else:
            st.info("Pick a template from the dropdown first.")

    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.text_input("Title", key="ti_title")
        # Feature 2: category dropdown remembers previously used categories.
        cat_options = st.session_state.known_categories + [NEW_CATEGORY]
        if st.session_state.ti_category_choice not in cat_options:
            st.session_state.ti_category_choice = cat_options[0]
        st.selectbox("Category", cat_options, key="ti_category_choice")
    with tc2:
        st.number_input("Duration (min)", min_value=1, max_value=240, key="ti_duration")
        st.selectbox("Recurrence", ["daily", "weekly", "once"], key="ti_recurrence")
    with tc3:
        st.selectbox("Priority", ["high", "medium", "low"], key="ti_priority")
        st.text_input("Preferred time (optional)", key="ti_preftime")

    # Revealed only when "Add new category..." is chosen (works because these
    # are reactive widgets, not inside a form).
    new_category = ""
    if st.session_state.ti_category_choice == NEW_CATEGORY:
        new_category = st.text_input("New category name", key="ti_newcat")

    if st.button("Add task", type="primary"):
        title = st.session_state.ti_title.strip()
        if st.session_state.ti_category_choice == NEW_CATEGORY:
            category = new_category.strip()
        else:
            category = st.session_state.ti_category_choice

        if not title:
            st.warning("Please enter a task title.")
        elif not category:
            st.warning("Please enter a name for the new category.")
        else:
            # Remember any brand-new category for future dropdowns.
            if category not in st.session_state.known_categories:
                st.session_state.known_categories = sorted(
                    set(st.session_state.known_categories) | {category}
                )
            selected_pet.add_task(
                Task(
                    title=title,
                    duration_minutes=int(st.session_state.ti_duration),
                    priority=st.session_state.ti_priority,
                    recurrence=st.session_state.ti_recurrence,
                    category=category,
                    preferred_time=st.session_state.ti_preftime.strip() or None,
                )
            )
            set_flash("success", f"Added '{title}' to {selected_pet.name}!")
            # Keep the fields/template populated so the same task can be added to
            # another pet without retyping. If a brand-new category was just
            # created, select it (and drop the free-text input) on the next run.
            if st.session_state.ti_category_choice == NEW_CATEGORY:
                st.session_state._select_category_after_add = category
            st.rerun()

    # --- Edit / remove an existing task ---
    if selected_pet.tasks:
        with st.expander("Edit or remove a task"):
            task_labels = {f"[{t.id}] {t.title}": t.id for t in selected_pet.tasks}
            chosen_label = st.selectbox("Task", list(task_labels.keys()))
            task_id = task_labels[chosen_label]
            current = next(t for t in selected_pet.tasks if t.id == task_id)

            with st.form("edit_task_form"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    e_title = st.text_input("Title", value=current.title)
                with ec2:
                    e_duration = st.number_input(
                        "Duration (min)",
                        min_value=1,
                        max_value=240,
                        value=int(current.duration_minutes),
                    )
                with ec3:
                    e_priority = st.selectbox(
                        "Priority",
                        ["high", "medium", "low"],
                        index=["high", "medium", "low"].index(current.priority)
                        if current.priority in ("high", "medium", "low")
                        else 1,
                    )
                e_completed = st.checkbox("Completed", value=current.completed)

                save_col, del_col = st.columns(2)
                if save_col.form_submit_button("Save changes"):
                    was_completed = current.completed
                    selected_pet.edit_task(
                        task_id,
                        title=e_title.strip() or current.title,
                        duration_minutes=int(e_duration),
                        priority=e_priority,
                    )
                    if e_completed and not was_completed:
                        # Marking complete spawns the next occurrence for recurring tasks.
                        next_task = selected_pet.complete_task(task_id)
                        if next_task is not None:
                            set_flash(
                                "success",
                                f"Task completed. Next {next_task.recurrence} "
                                f"occurrence added (due {next_task.due_date}).",
                            )
                        else:
                            set_flash("success", "Task completed.")
                    elif not e_completed and was_completed:
                        selected_pet.edit_task(task_id, completed=False)
                        set_flash("success", "Task updated.")
                    else:
                        set_flash("success", "Task updated.")
                    st.rerun()
                if del_col.form_submit_button("Delete task"):
                    selected_pet.remove_task(task_id)
                    set_flash("info", "Task removed.")
                    st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Generate today's plan
# ---------------------------------------------------------------------------
st.subheader("Today's Plan")

if st.button("Generate schedule", type="primary"):
    # Persist so the filter widgets below can re-render results on their own
    # reruns without the user having to click "Generate schedule" again.
    st.session_state.plan_generated = True

if st.session_state.get("plan_generated"):
    scheduler = Scheduler(
        available_minutes=owner.available_minutes,
        start_time=st.session_state.start_time,
    )
    all_pairs = owner.get_all_tasks()  # flat [(pet, task), ...] across all pets

    if not all_pairs:
        st.info("No tasks to schedule yet. Add pets and tasks above.")
    else:
        # --- Filter controls, wired to Scheduler.filter_tasks() ---
        pet_options = ["All pets", *[p.name for p in owner.list_pets()]]
        if st.session_state.get("plan_pet_filter") not in pet_options:
            st.session_state.plan_pet_filter = "All pets"  # a filtered pet was removed
        fc1, fc2 = st.columns(2)
        with fc1:
            pet_filter = st.selectbox("Filter by pet", pet_options, key="plan_pet_filter")
        with fc2:
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "Incomplete only", "Completed only"],
                key="plan_status_filter",
            )
        pet_name = None if pet_filter == "All pets" else pet_filter
        completed = {"All": None, "Incomplete only": False, "Completed only": True}[status_filter]
        pairs = scheduler.filter_tasks(all_pairs, pet_name=pet_name, completed=completed)

        # --- Conflicts surfaced FIRST, as warnings (separate from success msgs) ---
        for warning in scheduler.detect_conflicts(pairs):
            st.warning("⚠️ " + warning)

        # --- Time-boxed schedule as a clean table ---
        plan = scheduler.generate_plan(pairs)
        if plan:
            st.markdown("**Today's Schedule**")
            st.dataframe(
                [
                    {
                        "Time": item.start_time,
                        "Pet": item.pet_name,
                        "Task": item.title,
                        "Duration (min)": item.duration_minutes,
                        "Priority": item.priority,
                    }
                    for item in plan
                ],
                hide_index=True,
                width="stretch",
            )
        elif not pairs:
            st.info("No tasks match the current filter.")
        else:
            st.info("No tasks fit within the available time.")

        with st.expander("Priority ranking (before time-boxing)"):
            ordered = scheduler.sort_tasks([task for _pet, task in pairs])
            st.table(
                [
                    {
                        "Task": t.title,
                        "Priority": t.priority,
                        "Score": t.priority_score(),
                        "Duration (min)": t.duration_minutes,
                    }
                    for t in ordered
                ]
            )

        st.markdown("**Why this plan**")
        st.text(scheduler.explain(plan))
