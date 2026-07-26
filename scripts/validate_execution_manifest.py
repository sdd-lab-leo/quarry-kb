#!/usr/bin/env python3
"""Minimal execution-manifest schema validator for Quarry KB change packages."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required") from exc


def validate(manifest_path: Path, schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise SystemExit("manifest must be a mapping")

    missing = [key for key in schema.get("required", []) if key not in manifest]
    if missing:
        raise SystemExit(f"missing required top-level keys: {missing}")

    workspace = manifest.get("workspace") or {}
    for key in ("project_name", "repo_path", "branch"):
        if key not in workspace:
            raise SystemExit(f"workspace missing required key: {key}")

    task = manifest.get("task") or {}
    for key in ("title", "objective", "mode", "sdd_profile"):
        if key not in task:
            raise SystemExit(f"task missing required key: {key}")
    if task.get("sdd_profile") != "quarry-kb-fastapi-vue":
        raise SystemExit("task.sdd_profile must be quarry-kb-fastapi-vue")
    if task.get("mode") not in {"docs-only", "code-change", "review", "migration", "research"}:
        raise SystemExit(f"invalid task.mode: {task.get('mode')}")

    inputs = manifest.get("inputs") or {}
    for key in ("source_references", "documents", "adrs"):
        if key not in inputs:
            raise SystemExit(f"inputs missing required key: {key}")

    constraints = manifest.get("constraints") or {}
    for key in ("allowed_paths", "forbidden_paths", "external_actions_require_approval"):
        if key not in constraints:
            raise SystemExit(f"constraints missing required key: {key}")

    outputs = manifest.get("outputs") or {}
    for key in ("expected_artifacts", "completion_report"):
        if key not in outputs:
            raise SystemExit(f"outputs missing required key: {key}")

    verification = manifest.get("verification") or {}
    for key in ("commands", "quality_gates"):
        if key not in verification:
            raise SystemExit(f"verification missing required key: {key}")

    stop_conditions = manifest.get("stop_conditions")
    if not isinstance(stop_conditions, list) or not stop_conditions:
        raise SystemExit("stop_conditions must be a non-empty list")

    if "status" not in manifest:
        raise SystemExit("status is required by Quarry hand-off playbook")
    if "out_of_scope" not in manifest:
        raise SystemExit("out_of_scope is required by Quarry hand-off playbook")

    print(f"manifest OK: {manifest_path}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_execution_manifest.py <manifest.yaml>")
    root = Path(__file__).resolve().parents[1]
    validate(Path(sys.argv[1]).resolve(), root / "docs/00-context/execution-manifest.schema.json")


if __name__ == "__main__":
    main()
