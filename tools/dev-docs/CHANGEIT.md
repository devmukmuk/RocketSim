# tools/dev-docs/CHANGEIT.md

1. **Purpose**
   <pre lang="markdown">
   ChangeIt is the standardized implementation workflow for:
   - bug fixes
   - enhancements
   - refactors
   - small feature additions

   When the user says:
   "changeit"

   the assistant should:
   - analyze the requested change
   - infer implementation scope
   - generate git/github workflow commands
   - generate branch naming
   - generate issue/PR templates
   - follow project commit conventions
   </pre>

1. **Assistant Responsibilities**
   <pre lang="markdown">
   The assistant should:

   - Review current git status
   - Infer likely module and scope
   - Suggest branch names
   - Suggest issue titles
   - Generate issue bodies
   - Generate commit messages
   - Generate PR templates
   - Generate git workflow commands
   - Prefer pytest before commit
   - Prefer git add .
   - Avoid runtime/generated files unless intentional
   </pre>

1. **Command Output Rules**
   <pre lang="markdown">
   When generating terminal commands:

   - ALWAYS use plain fenced markdown code blocks
   - Prefer ```bash fenced blocks
   - NEVER use writing blocks for terminal commands
   - NEVER interleave commentary inside command blocks
   - Output must be directly copy/paste safe for Git Bash

   Example:

   ```bash
   git status
   pytest
   git add .

1. **Commit Style Conventions**
   <pre lang="markdown">
   Preferred commit formats:

   feat(module): description
   fix(module): description
   refactor(module): description
   docs(module): description
   test(module): description

   Examples:

   feat(validateit): add repair execution workflow
   fix(scanit): repair orphan sidecar cleanup
   refactor(photoit): simplify rename provider logic
   </pre>

1. **Branch Naming Conventions**
   <pre lang="markdown">
   Branch names should NOT contain GitHub issue numbers.

   Preferred:

   rocket-model-phase-1a
   motor-model-phase-1b
   simulation-phase-2a

   Or shorter:

   p1a-rocket-model
   p1b-motor-model
   p2a-flight-simulation

   Avoid:

   5-rocket-model-phase-1a
   17-motor-model-phase-1b

   Reason:

   - GitHub issue numbers are not known during planning
   - Branch names should remain stable
   - Branches should describe implementation scope
   - Phase identifiers already provide traceability

   The assistant should infer branch names from:
   - feature name
   - phase number
   - story identifier

   and should not require the user to provide issue numbers.
   </pre>

1. **Canonical Workflow Template**
   <pre lang="bash">
   BRANCH=""
   ISSUE_TITLE=""
   ISSUE_BODY=""
   COMMIT_MESSAGE=""

   ISSUE_URL=$(gh issue create \
     --title "$ISSUE_TITLE" \
     --body "$ISSUE_BODY")

   ISSUE_NUMBER=$(basename "$ISSUE_URL")

   git checkout main
   git pull origin main
   git checkout -b "$BRANCH"

   git add .

   git status
   pytest || exit 1

   git commit -m "$COMMIT_MESSAGE"

   git push -u origin "$BRANCH"

   gh pr create \
     --base main \
     --head "$BRANCH" \
     --title "$ISSUE_TITLE" \
     --body "
   ## Why
   - ...

   ## What
   - ...

   ## Impact
   - ...

   Closes #$ISSUE_NUMBER
   "
   </pre>

1. **Post Merge Cleanup**
   <pre lang="bash">
   After the PR is merged, use POSTMERGE.md.
   </pre>

1. **Workflow Preferences**
   <pre lang="markdown">
   Prefer:
   - small incremental phases
   - PR-friendly changes
   - test-first validation
   - provider/service separation
   - workflow orchestration patterns
   - minimal-risk implementation steps

   Avoid:
   - large multi-feature commits
   - direct pushes to main
   - mixing refactors with unrelated fixes
   - committing generated runtime files
   </pre>

<br>Author: Mike Mattinson/Chat  
<br>Created: May/20/2026
<br>Updated: Jun/11/2026