"""The deploy workflow keeps its safety properties: its triggers, its secrets and who signs.

A deploy holds the host's token, so each property that keeps it safe has a test: no trigger a pull
request can reach, every secret only in the deploy job and only there the protected environment,
the right to sign only in the attest job, every job on main only, a running deploy never
cancelled, and every action pinned by a full commit SHA.

There is no YAML library here, so deploy.yml is read as text, as the gate test reads ci.yml.
"""

import re
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "deploy.yml"
JOB = re.compile(r"^  ([a-z][a-z0-9_-]*):\n", re.MULTILINE)
TOP_KEY = re.compile(r"^([a-z_-]+):", re.MULTILINE)


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _head() -> str:
    """Everything before `jobs:`."""
    return _text().split("\njobs:\n", 1)[0]


def _jobs() -> dict[str, str]:
    parts = JOB.split(_text().split("\njobs:\n", 1)[1])
    jobs = {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}
    assert set(jobs) == {"build", "attest", "deploy"}, f"deploy.yml read as jobs {sorted(jobs)}"
    return jobs


def _on_block() -> str:
    head = _head()
    start = head.index("\non:\n") + len("\non:\n")
    following = TOP_KEY.search(head, start)
    return head[start : following.start() if following else len(head)]


def test_only_a_push_to_main_or_a_manual_run_triggers_it() -> None:
    block = _on_block()
    triggers = set(re.findall(r"^  ([a-z_]+):", block, re.MULTILINE))
    assert triggers == {"push", "workflow_dispatch"}
    assert re.search(r"^  push:\n    branches: \[main\]\n", block, re.MULTILINE)
    assert "pull_request" not in _text()


def test_every_job_runs_on_main_only() -> None:
    for name, block in _jobs().items():
        assert "    if: github.ref == 'refs/heads/main'\n" in block, (
            f"{name} is not limited to main"
        )


def test_secrets_and_the_environment_are_only_in_the_deploy_job() -> None:
    assert "secrets." not in _head()
    jobs = _jobs()
    holders = {name for name, block in jobs.items() if "secrets." in block}
    assert holders == {"deploy"}
    environments = {name for name, block in jobs.items() if "\n    environment:" in block}
    assert environments == {"deploy"}
    assert "\n      name: production\n" in jobs["deploy"]


def test_only_the_attest_job_can_sign() -> None:
    assert "id-token" not in _head()
    signers = {name for name, block in _jobs().items() if "id-token: write" in block}
    assert signers == {"attest"}


def test_the_workflow_grants_nothing_by_default_and_never_cancels_a_deploy() -> None:
    head = _head()
    assert "\npermissions: {}\n" in head
    assert "  cancel-in-progress: false\n" in head


def test_every_action_is_pinned_by_a_full_commit_sha() -> None:
    uses = re.findall(r"uses: (\S+)", _text())
    assert uses, "deploy.yml uses no action"
    unpinned = [use for use in uses if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", use)]
    assert not unpinned, f"not pinned by SHA: {unpinned}"
