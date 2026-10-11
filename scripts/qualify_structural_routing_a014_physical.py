from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.model import ModelAdapterError, ModelDescriptor, OllamaModelAdapter
from flywire_asca.structural_routing import RoutingPolicy
from flywire_asca.structural_routing.benchmark import (
    benchmark_report_payload,
    classify_a014_architecture,
    run_a014_benchmark,
)
from flywire_asca.structural_routing.benchmark_fixture import (
    EXPECTED_A014_FIXTURE_FINGERPRINT,
)
from flywire_asca.structural_routing.model_router import router_prompt_fingerprint


MODEL_NAME = "qwen3.5:4b"
EXPECTED_DIGEST = "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd"
EVIDENCE_ROLE = "physical_model_capability"
FIXTURE_VERSION = "a014-bilingual-v1"


def _run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _canonical_sha(payload: object) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def a014_source_manifest(
    *, root: Path = ROOT, ref: str = "HEAD"
) -> tuple[tuple[str, str, str], ...]:
    output = _run_git(root, "ls-tree", "-r", "--full-tree", ref)
    selected: list[tuple[str, str, str]] = []
    for line in output.splitlines():
        if not line:
            continue
        metadata, path = line.split("\t", 1)
        mode, object_type, blob_sha = metadata.split()
        if object_type != "blob":
            continue
        in_package = (
            path.startswith("src/flywire_asca/structural_routing/")
            and path.endswith(".py")
        )
        in_scripts = path in {
            "scripts/qualify_structural_routing_a014.py",
            "scripts/qualify_structural_routing_a014_physical.py",
        }
        if in_package or in_scripts:
            selected.append((mode, path, blob_sha))
    return tuple(sorted(selected, key=lambda item: item[1]))


def a014_source_manifest_fingerprint(
    *, root: Path = ROOT, ref: str = "HEAD"
) -> str:
    return _canonical_sha(a014_source_manifest(root=root, ref=ref))


def _descriptor_payload(descriptor: ModelDescriptor) -> dict[str, object]:
    payload = asdict(descriptor)
    payload["name"] = payload.pop("model_name")
    payload["digest"] = payload.pop("model_digest")
    payload["capabilities"] = list(descriptor.capabilities)
    return payload


def _invalid_payload(
    errors: list[str],
    *,
    source_sha: str | None = None,
    source_manifest_fingerprint: str | None = None,
) -> dict[str, object]:
    return {
        "qualification_scope": "physical_structural_routing_a014",
        "fixture_version": FIXTURE_VERSION,
        "evidence_role": EVIDENCE_ROLE,
        "model_capability_qualified": False,
        "physical_evidence": True,
        "experiment_valid": False,
        "errors": errors,
        "source": {
            "git_sha": source_sha,
            "manifest_fingerprint": source_manifest_fingerprint,
        },
        "fixture_fingerprint": EXPECTED_A014_FIXTURE_FINGERPRINT,
        "prompt_fingerprint": router_prompt_fingerprint(),
        "model": None,
        "benchmark": None,
        "physical_architecture_decision": None,
    }


def run_physical_qualification(
    *,
    adapter,
    expected_source_sha: str,
    root: Path = ROOT,
) -> dict[str, object]:
    root = Path(root)
    try:
        observed_head = _run_git(root, "rev-parse", "HEAD")
    except (subprocess.CalledProcessError, OSError) as exc:
        return _invalid_payload([f"unable to read source SHA: {exc}"])

    if observed_head != expected_source_sha:
        return _invalid_payload(
            [
                "source SHA mismatch: "
                f"expected {expected_source_sha}, observed {observed_head}"
            ],
            source_sha=observed_head,
        )

    try:
        manifest = a014_source_manifest(root=root, ref=expected_source_sha)
        manifest_fingerprint = a014_source_manifest_fingerprint(
            root=root, ref=expected_source_sha
        )
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        return _invalid_payload(
            [f"unable to bind source manifest: {exc}"],
            source_sha=observed_head,
        )

    if not manifest:
        return _invalid_payload(
            ["A014 source manifest is empty"],
            source_sha=observed_head,
            source_manifest_fingerprint=manifest_fingerprint,
        )

    try:
        descriptor = adapter.inspect()
    except ModelAdapterError as exc:
        return _invalid_payload(
            [f"model inspect failed: {exc}"],
            source_sha=observed_head,
            source_manifest_fingerprint=manifest_fingerprint,
        )

    identity_errors: list[str] = []
    if descriptor.model_name != MODEL_NAME:
        identity_errors.append(
            f"model name mismatch: expected {MODEL_NAME}, observed {descriptor.model_name}"
        )
    if descriptor.model_digest != EXPECTED_DIGEST:
        identity_errors.append(
            "model digest mismatch: "
            f"expected {EXPECTED_DIGEST}, observed {descriptor.model_digest}"
        )
    if identity_errors:
        return _invalid_payload(
            identity_errors,
            source_sha=observed_head,
            source_manifest_fingerprint=manifest_fingerprint,
        )

    adapters = {
        RoutingPolicy.RULE_ONLY: None,
        RoutingPolicy.MODEL_ONLY: adapter,
        RoutingPolicy.HYBRID_RULE_THEN_MODEL: adapter,
    }
    report = run_a014_benchmark(adapters_by_policy=adapters)
    report = replace(report, physical_evidence_bound=True)
    benchmark = benchmark_report_payload(report)
    decision = classify_a014_architecture(report).value

    payload: dict[str, object] = {
        "qualification_scope": "physical_structural_routing_a014",
        "fixture_version": FIXTURE_VERSION,
        "evidence_role": EVIDENCE_ROLE,
        "model_capability_qualified": True,
        "physical_evidence": True,
        "experiment_valid": True,
        "errors": [],
        "source": {
            "git_sha": expected_source_sha,
            "manifest": [list(item) for item in manifest],
            "manifest_fingerprint": manifest_fingerprint,
        },
        "fixture_fingerprint": report.fixture_fingerprint,
        "prompt_fingerprint": report.prompt_fingerprint,
        "model": _descriptor_payload(descriptor),
        "benchmark": benchmark,
        "physical_architecture_decision": decision,
    }
    payload["physical_evidence_sha256"] = _canonical_sha(payload)
    return payload


def _emit(payload: dict[str, object], output_path: Path | None) -> None:
    data = (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        stream.write(data)
        stream.flush()
    else:
        sys.stdout.write(data.decode("utf-8"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-source-sha", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    adapter = OllamaModelAdapter(
        MODEL_NAME,
        expected_digest=EXPECTED_DIGEST,
        timeout_seconds=120.0,
        keep_alive="10m",
    )
    payload = run_physical_qualification(
        adapter=adapter,
        expected_source_sha=args.expected_source_sha,
        root=ROOT,
    )
    _emit(payload, args.output)
    return 0 if payload.get("experiment_valid") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
