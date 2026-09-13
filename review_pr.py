"""
The reviewer that a GitHub Actions workflow calls automatically on every
pull_request event (opened / synchronize / reopened) — no human runs this.

Usage: python review_pr.py <base_ref> <head_ref>

Checks two things:
  1. Do the tests still pass on the PR's code? (the real checker)
  2. Did the diff remove a null/None-safety check? (a heuristic that
     catches risky patterns even when a test doesn't happen to cover it)

Writes review_comment.md — what a GitHub Action would post as a PR
comment — and exits non-zero if anything looks wrong.
"""
import re
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    base_ref, head_ref = sys.argv[1], sys.argv[2]

    diff = run(["git", "diff", f"{base_ref}..{head_ref}"]).stdout

    findings = []

    # Heuristic: flag removed null/None guard lines
    removed_lines = [l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
    null_check_pattern = re.compile(r"is\s+None|is\s+null|!=\s*null|not\s+\w+\s*:", re.IGNORECASE)
    for line in removed_lines:
        if null_check_pattern.search(line):
            findings.append(f"Removed a null-safety check: `{line[1:].strip()}`")

    # Real checker: run the test suite on the PR's code
    test_result = run(["python3", "-m", "unittest", "test_inventory.py"])
    tests_pass = test_result.returncode == 0
    if not tests_pass:
        findings.append("Test suite fails on this PR:\n```\n" + test_result.stderr.strip() + "\n```")

    verdict = "FAIL" if findings else "PASS"

    with open("review_comment.md", "w") as f:
        f.write(f"## Automated PR Review — {verdict}\n\n")
        if findings:
            f.write("This PR was flagged:\n\n")
            for finding in findings:
                f.write(f"- {finding}\n")
        else:
            f.write("No issues found. Tests pass and no risky patterns detected.\n")

    print(open("review_comment.md").read())
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
