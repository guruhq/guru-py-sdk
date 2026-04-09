# Skill: Complete Iteration

## When to Use
After completing a unit of work. Creates both an implementation close-out and a learnings doc.

## Instructions

### 1. Run quality gates
Run `make check` (lint + typecheck + test). All must pass before closing out.

### 2. Close out the implementation record
1. Read the current iteration doc in `docs/implementation/NNN-*.md`
2. Update **Status** to "Complete"
3. Add these sections:
   - **What We Actually Built**: What was delivered (may differ from plan)
   - **What Changed From Plan**: Any deviations and why
   - **Test Coverage**: Summary of tests added/modified

### 3. Create a learnings doc
1. Create `docs/learnings/NNN-iteration-title-learnings.md` with:
   - **What Worked**: Approaches, tools, or patterns that were effective
   - **What Didn't Work**: Problems encountered, dead ends
   - **Patterns That Emerged**: Reusable patterns discovered during the work
   - **What We'd Do Differently**: Hindsight improvements

### 4. Update architecture
1. Run the `update-architecture` skill if architecture changed (new resources, new layers, new dependencies)

### 5. Update CLAUDE.md
1. If new patterns or rules emerged, add them to the "Patterns and Rules" section in CLAUDE.md
