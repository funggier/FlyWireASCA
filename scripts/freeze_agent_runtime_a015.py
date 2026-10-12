"""Freeze or independently check the approved A015 bilingual input artifact."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from project_asca.evaluation.fixture import load_frozen_workload,bounds_from_workload
from project_asca.evaluation.freeze import validate_freeze,write_freeze_lock

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fixture",type=Path,default=Path("fixtures/a015/stage-a-v1"))
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    try:
        w=load_frozen_workload(args.fixture)
        if args.check and not w.lock:raise ValueError("freeze lock absent")
        v=validate_freeze(w,bounds_from_workload(w))
        if not v.valid:raise ValueError(repr(v.errors))
        if not args.check:write_freeze_lock(args.fixture,v)
        print(json.dumps({"valid":v.valid,"aggregate_hash":v.aggregate_hash,"cases":len(w.cases),
                         "max_prompt_upper_bound":v.max_prompt_upper_bound,
                         "context_with_output":v.max_prompt_upper_bound+1024}))
        return 0
    except (ValueError,KeyError,TypeError) as exc:
        print(json.dumps({"valid":False,"error":str(exc)}));return 1

if __name__=="__main__":raise SystemExit(main())
