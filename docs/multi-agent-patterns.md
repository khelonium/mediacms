# Multi-Agent Patterns for Claude Code

Reference documentation for orchestrating multi-agent workflows within Claude Code sessions.

## Three Patterns

### 1. Supervisor / Orchestrator

A single coordinator dispatches tasks to specialist agents and synthesizes their outputs.

**Structure:**
```
Orchestrator
├── Agent A (research)
├── Agent B (implementation)
└── Agent C (validation)
```

**When to use:**
- Tasks with clear decomposition into independent subtasks
- When a central authority needs to merge results
- Fan-out/fan-in workflows (e.g., search multiple codebases, then combine findings)

**Claude Code implementation:**
- Main conversation acts as orchestrator
- Use `Agent` tool with `subagent_type: "Explore"` or `"general-purpose"` for specialist work
- Use `run_in_background: true` for parallel independent agents

### 2. Peer-to-Peer / Swarm

Multiple agents with equal authority collaborate, each contributing their specialty.

**Structure:**
```
Agent A <──> Agent B
   ↕            ↕
Agent C <──> Agent D
```

**When to use:**
- Brainstorming or multi-perspective analysis
- When no single agent has full authority
- Consensus-building tasks

**Claude Code implementation:**
- Launch multiple `Agent` calls in a single message for parallel execution
- Each agent gets a different perspective/role in its prompt
- Main conversation synthesizes their outputs

### 3. Hierarchical (Strategy -> Planning -> Execution)

Layered approach where strategy informs planning, which drives execution.

**Structure:**
```
Strategy Layer (PO + PM)
    ↓
Planning Layer (Dev + QA design)
    ↓ [user approval gate]
Execution Layer (Dev implements + QA verifies)
```

**When to use:**
- Feature implementation requiring multiple roles
- When user approval is needed before execution
- Complex changes touching multiple system layers (DB, API, frontend)

**Claude Code implementation:**
- Phase 1 runs in plan mode (`EnterPlanMode`)
- Roles are sequential prompts within the same conversation
- `TaskCreate`/`TaskUpdate` track progress across phases
- `ExitPlanMode` gates user approval between phases
- See `.claude/skills/implement-feature.md` for a working example

## Decision Matrix

| Factor | Supervisor | Peer-to-Peer | Hierarchical |
|--------|-----------|--------------|--------------|
| Task complexity | Medium | Low-Medium | High |
| Need for user approval | No | No | Yes |
| Role specialization | Moderate | Low | High |
| Token cost | Medium (~5x) | Medium (~5x) | High (~15x) |
| Best for | Research, refactoring | Code review, analysis | Feature implementation |

## Reusable Role Definitions

### Product Owner (PO)
- Refines requirements from user input
- Asks clarifying questions via `AskUserQuestion`
- Outputs user stories with acceptance criteria
- Focus: *what* to build and *why*

### Senior Developer (Dev)
- Explores codebase to find patterns and affected files
- Designs technical approach (data model, API, frontend)
- Implements code changes
- Focus: *how* to build it

### QA Engineer
- Writes Given/When/Then test scenarios
- Covers happy path, edge cases, permissions, regressions
- Verifies implementation against acceptance criteria
- Runs test suite and linting
- Focus: *does it work correctly*

### Project Manager (PM)
- Synthesizes all role outputs into an ordered task list
- Sets up task dependencies
- Tracks progress via `TaskCreate`/`TaskUpdate`
- Focus: *in what order* and *is it on track*

## Claude Code Implementation Notes

### Skills = Structured Markdown Prompts
Skills (`.claude/skills/*.md`) are markdown files that define multi-step workflows. They are invoked via `/skill-name` and provide structured instructions that Claude follows.

### Agents = Role Prompts Within Phases
Within a skill, different "roles" are implemented as sections of the prompt that Claude executes sequentially. The `Agent` tool can be used for parallel exploration tasks.

### State = TaskCreate / TaskUpdate
Task progress is tracked using the built-in task management tools:
- `TaskCreate` — define work items with descriptions and active forms
- `TaskUpdate` — set status (`pending` -> `in_progress` -> `completed`), add dependencies
- `TaskList` — view all tasks and their states
- `TaskGet` — get full details of a specific task

### Token Economics
- Single agent: ~1x baseline
- Supervisor pattern: ~5x (multiple agent calls)
- Hierarchical pattern: ~15x (multiple phases, roles, and verification)
- Use `model: "haiku"` parameter on `Agent` calls for quick/simple subtasks to reduce cost
