"""Offline source/evidence verification; never generation or embedding."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from project_asca.evaluation.evidence import load_evidence,verify_evidence
def verify_file(path,*,root=None):
    root=Path(root) if root else Path(__file__).resolve().parents[1]
    evidence=load_evidence(path);return evidence,verify_evidence(evidence,root=root)
def main():
    parser=argparse.ArgumentParser();parser.add_argument("evidence",type=Path)
    args=parser.parse_args()
    try:
        evidence,validation=verify_file(args.evidence)
        print(json.dumps({"valid":validation.valid,"physical":validation.physical,
            "usage_complete":validation.usage_complete,"outcome":evidence.outcome.value,
            "trials":len(evidence.trials),"source_fingerprint":evidence.metadata.source.fingerprint,
            "errors":validation.errors}))
        return 0 if validation.valid else 1
    except (ValueError,OSError) as exc:
        print(json.dumps({"valid":False,"errors":[str(exc)]}));return 1
if __name__=="__main__":raise SystemExit(main())
