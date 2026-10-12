"""Replay preserved v1 evidence at its pinned source; never qualifies current HEAD."""
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path

V1_BEHAVIOR="c968330cf97d7a7c7893aa70fddd150ce8dd510e"
V1_PAYLOAD="8036befcd0532b59e047ca6fb5c78b5f9a4f6895b2a84bad97b4ee26fc0241ad"
V1_SOURCE="e5d6f1f08735b8292b05bbf4b40135995af2c62b17e927a6d78c73ddd03c375b"
LIMITATIONS=(
    "v1 interpretation could omit request clauses",
    "v1 single-output/publication/replay controls had independent-review defects",
    "v1 model-facing wire schema was incomplete",
    "original-v1 replay does not qualify corrected current source",
)

def replay_history(path,*,root=None):
    root=Path(root or Path(__file__).resolve().parents[1]).resolve()
    path=Path(path).resolve()
    raw=json.loads(path.read_text(encoding="utf-8"))
    if (raw.get("payload_hash")!=V1_PAYLOAD
        or raw.get("metadata",{}).get("behavior_commit")!=V1_BEHAVIOR
        or raw.get("metadata",{}).get("source",{}).get("fingerprint")!=V1_SOURCE):
        raise ValueError("not the preserved pinned v1 artifact")
    git=["git","-c","core.longpaths=true","-c","core.autocrlf=false"]
    env=os.environ.copy();env.pop("PYTHONPATH",None)
    with tempfile.TemporaryDirectory(prefix="asca-a015-history-") as folder:
        checkout=Path(folder)/"source"
        subprocess.run(git+["clone","-c","core.longpaths=true","-c","core.autocrlf=false","--quiet","--local","--no-hardlinks","--no-checkout",str(root),str(checkout)],
                       check=True,capture_output=True,text=True,env=env)
        subprocess.run(git+["-C",str(checkout),"checkout","--quiet","--detach",V1_BEHAVIOR],
                       check=True,capture_output=True,text=True,env=env)
        head=subprocess.check_output(git+["-C",str(checkout),"rev-parse","HEAD"],text=True,env=env).strip()
        if head!=V1_BEHAVIOR:raise ValueError("historical checkout identity")
        result=subprocess.run([sys.executable,"-X","utf8",str(checkout/"scripts/verify_a015_physical_evidence.py"),str(path)],
                              cwd=checkout,env=env,capture_output=True,text=True,encoding="utf-8")
        try:validation=json.loads(result.stdout)
        except ValueError as exc:raise ValueError("historical verifier output") from exc
        if (result.returncode or not validation.get("valid") or not validation.get("physical")
            or not validation.get("usage_complete") or validation.get("trials")!=384
            or validation.get("source_fingerprint")!=V1_SOURCE):
            raise ValueError("historical v1 replay failed: "+str(validation.get("errors",())))
    return {"status":"VALID_UNDER_ORIGINAL_V1_CONTRACT","behavior_commit":V1_BEHAVIOR,
            "payload_hash":V1_PAYLOAD,"source_fingerprint":V1_SOURCE,"trials":384,
            "original_outcome":validation["outcome"],"current_source_qualified":False,
            "review_limitations":LIMITATIONS}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("evidence",type=Path)
    args=parser.parse_args()
    try:
        print(json.dumps(replay_history(args.evidence)));return 0
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        print(json.dumps({"status":"HISTORICAL_V1_REPLAY_FAILED","current_source_qualified":False,"errors":[str(exc)]}));return 1
if __name__=="__main__":raise SystemExit(main())
