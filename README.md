# The Doorbell Loop

A loop that reacts to a pull request — no prompt typed. Uses GitHub
Actions' `pull_request` event as the event-driven heartbeat.

## Important: this needs a real GitHub repo

Unlike Projects 1–5, this can't be fully demonstrated in a sandbox —
it requires GitHub's actual webhook infrastructure to fire. Everything
here has been proven **locally** with real git branches and a real
crashing bug; the last section tells you exactly how to wire it to a
real repo so GitHub fires it for you.

## Repository contents

| File | Purpose |
|---|---|
| `inventory.py` / `test_inventory.py` | Real code with a null-safety check, and tests covering it |
| `review_pr.py` | The reviewer — runs tests on the PR's actual code (via worktree) + flags removed null-checks |
| `.github/workflows/pr-review.yml` | The GitHub Action — fires on PR opened/synchronize/reopened, posts the review as a PR comment |

## The planted bug

The "bad" PR removes this line from `find_item`:
```python
if items is None:
    return None
```
Without it, calling `find_item(None, 1)` crashes with
`TypeError: 'NoneType' object is not iterable` instead of returning
`None` — a classic deleted-null-check bug.

## Proof (both required outcomes, tested locally)

**Harmless PR → PASS:**
```
## Automated PR Review — PASS
No issues found. Tests pass and no risky patterns detected.
```

**Planted-bug PR → FAIL, with a reason:**
```
## Automated PR Review — FAIL
This PR was flagged:
- Removed a null-safety check: `if items is None:`
```
(The test suite also genuinely crashes on this branch — confirmed with
`python3 -m unittest test_inventory.py -v`.)

## Setting this up for real (so GitHub fires it, not you)

1. Push this repo to GitHub (a throwaway/test repo is fine).
2. The workflow file is already at `.github/workflows/pr-review.yml` —
   GitHub picks it up automatically once it's on the default branch.
3. Create a branch, remove the null check from `inventory.py` (or plant
   any similar bug — an off-by-one works the same way), push it, and
   open a PR.
4. **Don't run anything yourself.** Within a minute, GitHub runs the
   workflow and posts a comment on the PR — that's the review you
   never asked for.
5. Push another commit to the same PR branch. The workflow fires again
   automatically (the `synchronize` event) — that re-fire is the event
   heartbeat working, same as the assignment describes.

## Two other ways to get the same result

- **OpenCode approach:** run `opencode github install` in the repo and
  accept the workflow it generates — it does the same job, generated
  for you instead of hand-written here.
- **Claude Code approach:** create a Routine with a GitHub pull-request
  trigger (see the loop-engineering crash course appendix on Routines
  for the exact filter options).

Either replaces `review_pr.py`'s heuristics with a full AI code review,
if you want something smarter than pattern-matching.

## Why the reviewer needs BOTH checks

Early in building this, testing the "bad" branch's code with the
wrong working directory checked out made it look like tests still
passed — a false PASS, for a reason that had nothing to do with the
bug. Fixed by running tests inside an isolated worktree of the actual
head ref, not wherever the shell happened to be. Same lesson as
Project 4's reviewer: a checker is only as good as what it actually
inspects.

## Completing the four heartbeats

With Projects 1–3 (in-session, conditional, scheduled) and this one
(event-driven), all four heartbeat types from the crash course are
now covered by something you've actually built and run.
