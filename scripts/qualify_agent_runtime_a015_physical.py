"""Run the approved fixed native protocol after clean G4 preflight."""
import argparse,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from project_asca.evaluation.fixture import load_frozen_workload
from project_asca.evaluation.physical import run_physical_comparison
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_a015_physical_evidence import verify_file
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fixture",type=Path,default=Path("fixtures/a015/stage-a-v1"))
    parser.add_argument("--repetitions",type=int,choices=(3,),default=3)
    parser.add_argument("--seed",type=int,choices=(0,),default=0)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    evidence=run_physical_comparison(load_frozen_workload(args.fixture),output=args.output,
                                     repetitions=args.repetitions,seed=args.seed)
    _,validation=verify_file(args.output)
    return 0 if validation.valid else 1
if __name__=="__main__":raise SystemExit(main())
