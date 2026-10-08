from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flywire_asca.familiarity import (
    benchmark_report_payload,
    build_a003_qualification_fixture,
    qualify_a003_report,
    run_familiarity_benchmark,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qualify", action="store_true")
    args = parser.parse_args()

    traces, cases = build_a003_qualification_fixture()
    report = run_familiarity_benchmark(traces, cases)
    payload = benchmark_report_payload(report)
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )

    if args.qualify:
        errors = qualify_a003_report(report)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
