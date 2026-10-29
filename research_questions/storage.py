"""Atomic and immutable file storage for research runs."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str)


def write_json_replace(path: Path, value: Any) -> None:
    atomic_write_text(path, json_text(value))


def write_json_once(path: Path, value: Any) -> None:
    """Write an immutable artifact, refusing to replace an existing file."""

    if path.exists():
        raise FileExistsError(f"Refusing to overwrite immutable artifact: {path}")
    atomic_write_text(path, json_text(value))


def write_text_once(path: Path, text: str) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite immutable artifact: {path}")
    atomic_write_text(path, text)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def aggregate_resources(records: Sequence[Mapping]) -> dict[str, Any]:
    failed = [record for record in records if record.get("request_status") == "failed"]
    costs = [record.get("cost_usd") for record in records]
    return {
        "calls": len(records),
        "successful_calls": len(records) - len(failed),
        "failed_calls": len(failed),
        "input_tokens": sum(int(record.get("input_tokens") or 0) for record in records),
        "output_tokens": sum(int(record.get("output_tokens") or 0) for record in records),
        "reasoning_tokens": sum(
            int(record.get("reasoning_tokens") or 0) for record in records
        ),
        "total_tokens": sum(int(record.get("total_tokens") or 0) for record in records),
        "cost_usd": round(sum(float(cost or 0) for cost in costs), 10),
        "exact_cost_complete": all(cost is not None for cost in costs)
        if records
        else None,
        "local_latency_ms": round(
            sum(float(record.get("local_latency_ms") or 0) for record in records), 3
        ),
    }


def transcript_markdown(events: Sequence[Mapping], completed_rounds: int) -> str:
    lines = ["# Public transcript", ""]
    for round_number in range(1, completed_rounds + 1):
        lines.extend([f"## Round {round_number}", ""])
        public_events = [
            event
            for event in events
            if event.get("round") == round_number
            and (
                (
                    str(event.get("type") or "").upper() in {"TALK", "OBSERVE"}
                    and str(event.get("content") or "").strip()
                )
                or str(event.get("type") or "").upper()
                in {"TAKE_SEAT", "LEAVE_SEAT"}
            )
        ]
        if not public_events:
            lines.extend(["_[No public speech recorded]_", ""])
        else:
            for event in public_events:
                lines.append(
                    f"- **Turn {event.get('turn')} — {event.get('agent')}:** "
                    f"{str(event.get('content')).strip()}"
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_round_scores_csv(evaluation_dir: Path, output_path: Path) -> None:
    rows: list[dict[str, Any]] = []
    for path in sorted(evaluation_dir.glob("*.json")):
        value = read_json(path)
        metadata = value["run"]
        evaluation = value["evaluation"]
        for round_score in evaluation["round_scores"]:
            peak_score = round_score.get(
                "peak_conflict_score", round_score.get("conflict_score")
            )
            remaining_score = round_score.get(
                "remaining_conflict_score", round_score.get("conflict_score")
            )
            rows.append(
                {
                    "scenario_id": metadata["scenario_id"],
                    "configuration_id": metadata["configuration_id"],
                    "run_id": metadata["run_id"],
                    "round": round_score["round"],
                    "peak_conflict_score": peak_score,
                    "remaining_conflict_score": remaining_score,
                    "movement": round_score.get("movement", "legacy_v1"),
                    "final_status": evaluation["final_status"],
                    "resolution_mechanism": evaluation.get(
                        "resolution_mechanism", "legacy_v1"
                    ),
                    "evaluator_model": metadata["evaluator_model"],
                    "prompt_version": value["evaluator"]["prompt_version"],
                }
            )
    if not rows:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(f".{output_path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output_path)


__all__ = [
    "aggregate_resources",
    "atomic_write_text",
    "file_sha256",
    "git_commit",
    "read_json",
    "transcript_markdown",
    "utc_now",
    "write_json_once",
    "write_json_replace",
    "write_round_scores_csv",
    "write_text_once",
]
