"""AC-3/AC-4: the import-linter architecture contracts pass (run from repo root)."""

import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Same entry point as the `lint-imports` console script, but invoked through the
# running interpreter so the test never depends on PATH containing .venv/bin
# (IDE runners, CI, tox). `lint_imports_command` is import-linter's documented
# console-script target; it discovers [tool.importlinter] via cwd=REPO_ROOT.
_LINT_IMPORTS = [
    sys.executable,
    "-c",
    "from importlinter.cli import lint_imports_command; lint_imports_command()",
]


def test_lint_imports_passes() -> None:
    """The import-linter contracts hold — domain purity + module boundaries.

    CI (Story 1.1c) wires the `lint-imports` console script; the README documents
    it as the local command as well.
    """
    result = subprocess.run(
        _LINT_IMPORTS,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"lint-imports failed:\n{result.stdout}\n{result.stderr}"


def test_domain_forbidden_list_covers_all_runtime_dependencies() -> None:
    """AD-2: every runtime dependency (except the allowed schema layer) is forbidden in src.domain.

    Guards the forbidden list in pyproject.toml against drifting out of sync
    with [project.dependencies]: a newly added dependency must be explicitly
    listed (or deliberately allowed here) before it is importable from the domain.
    """
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies: list[str] = pyproject["project"]["dependencies"]
    contracts: list[dict[str, object]] = pyproject["tool"]["importlinter"]["contracts"]
    forbidden = next(
        contract["forbidden_modules"]
        for contract in contracts
        if contract["type"] == "forbidden"
    )
    # Pydantic is deliberately allowed in the domain (schema-layer convention, see AD-2 comment).
    allowed_in_domain = {"pydantic"}
    for dependency in dependencies:
        name = dependency.split("==")[0]
        if name not in allowed_in_domain:
            assert name in forbidden, (
                f"Runtime dependency {name!r} is missing from the domain-purity forbidden "
                "list in pyproject.toml — add it (or allowlist it with a comment) to keep "
                "AD-2 enforced."
            )
