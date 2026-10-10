"""Local physical A011 entry point, including a fresh portable replay."""
from __future__ import annotations
from qualify_asca_v0x_a011 import argument_parser, build_context
from flywire_asca.qualification.artifacts import publish_pack
from flywire_asca.qualification.classifier import pack_exit_code
from flywire_asca.qualification.physical import OllamaRuntimeProbe, run_full
from flywire_asca.qualification.records import QualificationError
import sys


def main(argv=None):
    args = argument_parser("ASCA v0.x full-system qualification").parse_args(argv)
    context = None
    try:
        context = build_context(args)
        pack = run_full(context,OllamaRuntimeProbe())
        manifest,_ = publish_pack(context.store,pack)
        print(f"a011_engineering_verdict={pack.engineering_verdict.value}")
        print("qualification_scope=FULL_SYSTEM; is_final=true")
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
