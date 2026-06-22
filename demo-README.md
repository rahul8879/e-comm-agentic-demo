# CodeSentinel — Demo

Two approaches. Same task. Completely different results.

---

## What This Demo Shows

**Task:** Review PR #247 (payment code with bugs) and PR #248 (README update)

| | Workflow | Agentic |
|--|---------|---------|
| PR #247 | 3 fixed steps, generic report | Deep security check, specific line comments, PR blocked |
| PR #248 | 3 fixed steps, security check on README | Sees markdown → approves in 2 steps |
| Steps | Always same | Decided at runtime |
| Context | None | Reads team standards first |
| Memory | None | Tracks what it already checked |

---

## Setup

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
```

---

## Run

```bash
cd demo/

# Approach 1: Workflow — fixed steps
python approach_1_workflow.py

# Approach 2: Agentic — dynamic path
python approach_2_agentic.py
```

---

## What to Observe

### In approach_1_workflow.py

```
[Step 1] Getting files...
[Step 2] Running security check...    ← same for EVERY PR
[Step 3] Posting report...            ← even README gets this
```

Notice: PR #248 (README) goes through a full security check. Wasted.  
Notice: No specific line numbers in the report.  
Notice: You manually ran this — it didn't wake up on its own.

### In approach_2_agentic.py

```
── Agent Step 1 ──
  📄 read_file(team_standards.md)      ← agent decided this

── Agent Step 2 ──
  📂 list_pr_files(247)

── Agent Step 3 ──
  📄 read_file(users.py)

── Agent Step 4 ──
  📝 post_review_comment()
     File:     users.py:8
     Severity: P0
     Issue:    SQL injection via f-string
     Fix:      cursor.execute(query, (username, password))

── Agent Step 5 ──
  🚫 set_pr_status()
     PR:     #247
     Status: BLOCKED
```

Notice: Agent read `team_standards.md` first — nobody told it to.  
Notice: Specific line numbers and fixes.  
Notice: PR #248 gets approved in 2 steps — agent saw it was a README.

---

## The Key Question

> "Kaun sa step predetermined tha?"

**Workflow:** All of them. Always 3 steps.  
**Agent:** None of them. Agent decided each step based on previous observation.

That is the difference.

---

## Next

Session 2: We build this agent loop from scratch, line by line.  
Session 3: We add memory — agent remembers past PRs.
