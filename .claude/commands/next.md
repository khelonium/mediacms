# /next

Pick the top item from `ROADMAP.md` and implement it with a Senior Dev + QA team.

**Usage:** `/next`

---

## Phase 1 — Plan (runs in plan mode)

Enter plan mode with `EnterPlanMode`, then:

### Step 1: Pick the Next Item

1. Read `ROADMAP.md` and identify the first item under "## Up Next".
2. If "Up Next" is empty, tell the user "Nothing left on the roadmap!" and stop.
3. Display the picked item (name, why, scope, files) and confirm with the user via `AskUserQuestion`: "Ready to start on **[item name]**?"

### Step 2: Senior Developer — Technical Investigation

1. Use `Agent` with `subagent_type: "Explore"` to investigate the codebase for the scoped files listed in the roadmap item. The agent should:
   - Find all references to the feature being removed (imports, usages, templates, frontend components)
   - Identify any dependencies or side effects not listed in the roadmap scope
   - Check for database migrations that may be needed
2. Output a technical plan:
   - **Files to modify** (ordered list — backend first, then frontend, then templates)
   - **Files to delete** (if entire files become unnecessary)
   - **Migrations needed** (describe schema changes)
   - **Risk areas** (anything surprising found during investigation)

### Step 3: QA Engineer — Test Scenarios

1. Read the roadmap item scope and the Dev's technical plan.
2. Write Given/When/Then scenarios covering:
   - **Removal verification** — the feature is fully gone (no dead code, no broken references)
   - **Regressions** — existing features still work after removal
   - **Database** — migration applies cleanly, no orphaned data
   - **Frontend** — no broken imports, no dead routes, UI renders without errors
3. List the specific commands to verify (e.g., `pytest`, `flake8`, `npm run dist`).

### Step 4: Create Task List

1. Use `TaskCreate` for each implementation step with:
   - Clear `subject` in imperative form ("Remove socialaccount from INSTALLED_APPS")
   - Detailed `description` with what to change and which file to edit
   - `activeForm` in present continuous ("Removing socialaccount from INSTALLED_APPS")
2. Set up dependencies with `TaskUpdate` (`addBlockedBy`/`addBlocks`) where tasks must be sequential (e.g., migrations after model changes).
3. Write the plan file summarizing the technical plan and QA scenarios.
4. Call `ExitPlanMode` for user approval.

---

## Phase 2 — Implementation (after approval)

### Senior Developer

1. Call `TaskList` to see all tasks.
2. For each task (in dependency order):
   a. `TaskUpdate` to set `status: "in_progress"`
   b. Implement the changes (read files first, then edit)
   c. `TaskUpdate` to set `status: "completed"`
3. After all backend tasks: run `flake8` and `black --check .` to verify.
4. After all frontend tasks: run `npm run dist` in `frontend/` to verify the build.
5. Create database migration if schema changed: `python manage.py makemigrations`.

### QA Engineer

1. After all implementation tasks are complete:
   - Run `pytest` and report results
   - Run `flake8` and `black --check .`
   - If frontend was changed, verify `npm run dist` succeeds
   - Walk through each Given/When/Then scenario from Phase 1 and verify it passes by inspecting the code
2. If issues are found, fix them directly and re-verify.

---

## Phase 3 — Finalize

### Update Roadmap and Changelog

1. Read `ROADMAP.md` and remove the completed item from "## Up Next".
2. Read `docs/changelog.md` and add a new entry at the top following the existing format:
   - Use today's date as the section header (or append to today's section if it exists)
   - Use conventional commit format: `**chore(scope):** description`
3. Commit all changes with a conventional commit message: `chore(scope): remove [feature name]`

---

## Notes

- **Pattern:** This is a simplified Hierarchical pattern (Dev + QA only). The roadmap item provides the PO context; task ordering replaces the PM role.
- **Token awareness:** Uses ~10x tokens vs single-agent due to exploration + two-phase execution.
- **Scope:** This skill is designed for *removal* tasks. For adding new features, use `/implement-feature` instead.
