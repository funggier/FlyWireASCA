"""Portable A011 entry point. No runtime/model/threshold override."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT/"src") not in sys.path:
    sys.path.insert(0,str(ROOT/"src"))
if str(ROOT/"scripts") not in sys.path:
    sys.path.insert(0,str(ROOT/"scripts"))

from _a011_legacy_evidence import ALLOWLIST, load_legacy_validators
from flywire_asca.qualification.artifacts import ArtifactStore, publish_pack
from flywire_asca.qualification.classifier import pack_exit_code
from flywire_asca.qualification.portable import RunContext, run_portable
from flywire_asca.qualification.process import SubprocessRunner
from flywire_asca.qualification.profile import DEFAULT_PROFILE_PATH
from flywire_asca.qualification.records import QualificationError


class _Parser(argparse.ArgumentParser):
    def exit(self,status=0,message=None):
        if message:
            self._print_message(message,sys.stderr)
        raise SystemExit(0 if status == 0 else 1)


def build_context(args):
    root = (args.repo_root or ROOT).resolve()
    # The orchestrator/package and its children must use one checkout.
    if root != ROOT.resolve():
        raise QualificationError("SOURCE_MISMATCH", "--repo-root must identify the checkout executing this script")
    if re.fullmatch("[0-9a-f]{40}",args.expected_source_sha) is None:
        raise QualificationError("SOURCE_MISMATCH", "Expected source SHA must be exact 40-hex")
    profile = args.profile if args.profile is not None else root/DEFAULT_PROFILE_PATH
    if not profile.is_absolute():
        profile = root/profile
    store = ArtifactStore.create(root,args.output_dir)
    validators = {}
    for milestone in ALLOWLIST:
        def deferred(payload,milestone=milestone):
            # Load legacy code only after P00 has accepted source/profile.
            return load_legacy_validators(root)[milestone](payload)
        validators[milestone] = deferred
    return RunContext(root,args.expected_source_sha,profile,store,SubprocessRunner(),validators)


def argument_parser(description):
    parser = _Parser(description=description)
    parser.add_argument("--repo-root",type=Path)
    parser.add_argument("--expected-source-sha",required=True)
    parser.add_argument("--profile",type=Path)
    parser.add_argument("--output-dir",type=Path)
    return parser


def main(argv=None):
    args = argument_parser("ASCA v0.x portable qualification; nonfinal").parse_args(argv)
    context = None
    try:
        context = build_context(args)
        pack = run_portable(context)
        manifest,_ = publish_pack(context.store,pack)
        print(f"a011_portable_status={pack.portable_status.value}")
        print("qualification_scope=PORTABLE_ONLY; is_final=false; engineering_verdict=null")
        print(f"qualification_manifest={manifest}")
        print(f"qualified_behavior_sha={pack.source.commit}")
        return pack_exit_code(pack)
    except (QualificationError,OSError) as exc:
        code = exc.code if isinstance(exc,QualificationError) else "ARTIFACT_WRITE_FAILED"
        print(f"{code}: {exc}",file=sys.stderr)
        if context is not None:
            print(f"retained_diagnostics={context.store.root}",file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
