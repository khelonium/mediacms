# /implement-feature

Orchestrate feature implementation through PO, Senior Dev, PM, and QA roles using a hierarchical multi-agent pattern.

**Usage:** `/implement-feature <feature description>`

---

## Phase 1 — Plan (runs in plan mode)

Enter plan mode with `EnterPlanMode`, then execute each role sequentially:

### Role 1: Product Owner

1. Read the feature description from the user's message.
2. Use `AskUserQuestion` to ask 2-3 clarifying questions about scope, edge cases, and user expectations.
3. Write a refined user story with acceptance criteria:
   - **As a** [role] **I want** [action] **so that** [benefit]
   - Numbered acceptance criteria (AC-1, AC-2, ...)

### Role 2: Senior Developer

1. Use `Agent` with `subagent_type: "Explore"` to investigate:
   - Existing patterns to reuse (similar features already implemented)
   - Files that will need modification
   - Data model implications (new models, migrations, schema changes)
   - API endpoint conventions in the codebase
2. Output a technical design:
   - **Data model changes** (new models/fields, migration notes)
   - **API changes** (new endpoints, modified endpoints, permissions)
   - **Frontend changes** (new components, modified components, state management)
   - **Files to modify** (ordered list with brief description of changes per file)

### Role 3: QA Engineer

1. Read the PO's user story and Dev's technical design.
2. Write Given/When/Then test scenarios:
   - **Happy path** (main flow works end-to-end)
   - **Edge cases** (empty states, boundary values, concurrent operations)
   - **Permissions** (authorized vs unauthorized users, role-based access)
   - **Regressions** (existing features that could break)

### Role 4: Project Manager

1. Synthesize PO story + Dev design + QA scenarios into an ordered task list.
2. Use `TaskCreate` for each task with:
   - Clear `subject` in imperative form ("Add TechniqueMedia model to files/models.py")
   - Detailed `description` with what to implement and which files to touch
   - `activeForm` in present continuous ("Adding TechniqueMedia model")
3. Set up dependencies with `TaskUpdate` (`addBlockedBy`/`addBlocks`) where tasks must be sequential.
4. Write the plan file summarizing all roles' outputs.
5. Call `ExitPlanMode` for user approval.

---

## Phase 2 — Implementation (after approval)

### Role 1: Senior Developer

1. Call `TaskList` to see all tasks.
2. For each task (in dependency order):
   a. `TaskUpdate` to set `status: "in_progress"`
   b. Implement the changes (read files, edit/write code)
   c. Run linting if applicable (`flake8`, `black --check`)
   d. `TaskUpdate` to set `status: "completed"`
3. After all tasks are done, run the full build if frontend changes were made.

### Role 2: QA Engineer

1. After all implementation tasks are complete:
   - Run the test suite (`pytest` or equivalent)
   - Run linting (`flake8`, `black --check`)
   - Verify each Given/When/Then scenario from Phase 1 is satisfied by the code
   - Report any failing scenarios
2. If issues are found, create new tasks for fixes and repeat the Dev role.

---

## Notes

- **State management:** Task progress is tracked via `TaskCreate`/`TaskUpdate` — no external tools needed.
- **Token awareness:** Multi-agent orchestration uses ~15x more tokens than single-agent. Use `Agent` subagents for exploration/research only when the search scope is broad.
- **Pattern:** This is a Hierarchical pattern (Strategy -> Planning -> Execution). See `docs/multi-agent-patterns.md` for alternatives.
