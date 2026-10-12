"""Write clearly labeled portable engineering evidence without Ollama."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from project_asca.evaluation.fixture import load_frozen_workload
from project_asca.evaluation.portable import run_portable_qualification
from project_asca.agent_runtime.values import canonical_bytes
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fixture",type=Path,default=Path("fixtures/a015/stage-a-v1"))
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();result=run_portable_qualification(load_frozen_workload(args.fixture))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(canonical_bytes(result).decode("utf-8")+"\n",encoding="utf-8")
    print(json.dumps({"evidence_kind":result.evidence_kind,"physical":False,"scripted_usage":True,
       "engineering_valid":result.engineering_valid,"freeze_valid":result.freeze_valid,"trials":len(result.trials),
       "architecture_outcome":None,
       "completed":{k:v.completed for k,v in result.totals.variants.items()},
       "false_success":{k:v.false_success for k,v in result.totals.variants.items()}}))
    return 0 if result.engineering_valid else 1
if __name__=="__main__":raise SystemExit(main())
