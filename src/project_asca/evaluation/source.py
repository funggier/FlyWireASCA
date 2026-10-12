"""Read-only Git source identity and static package dependency closure."""
from dataclasses import dataclass
from pathlib import Path,PurePosixPath
import ast,subprocess,hashlib
from project_asca.agent_runtime.values import fingerprint
G2_COMMIT="7fc3c0ea901bfe49f9e788065bfc7de3626c0984"
SPEC_COMMIT="cccbf0fc47ca301bef8a6b7ac25398c2e1eb4447"
PLAN_COMMIT="4ca246df6976c7aa21ad07826017f167f0ee27da"
SPEC_PATH="docs/superpowers/specs/2026-10-12-a015-unified-agent-runtime-design.md"
SPEC_SHA256="ee4ab10cc4827381b494560704692c88de27822586e607ed20416cfbdfdffe91"
@dataclass(frozen=True,slots=True)
class SourceFingerprint:
    commit:str
    fingerprint:str
    files:tuple
    universe_hash:str
def git(root,*args,input=None):
    p=subprocess.run(["git",*args],cwd=root,input=input,capture_output=True)
    if p.returncode:raise ValueError("Git source inspection failed: "+p.stderr.decode("utf-8",errors="replace")[:400])
    return p.stdout
def tree(root,commit):
    rows={}
    for entry in git(root,"ls-tree","-r","-z",commit).split(b"\0"):
        if not entry:continue
        meta,path=entry.split(b"\t",1);mode,kind,blob=meta.decode("ascii").split()
        if kind=="blob":rows[path.decode("utf-8")]={"path":path.decode("utf-8"),"mode":mode,"blob":blob}
    return rows
def blobs(root,rows):
    names=[n for n in rows if n.endswith(".py")]
    data=git(root,"cat-file","--batch",input=("".join(rows[n]["blob"]+"\n" for n in names)).encode("ascii"))
    result={};position=0
    for name in names:
        end=data.index(b"\n",position);header=data[position:end].split();size=int(header[-1])
        result[name]=data[end+1:end+1+size];position=end+size+2
    return result
def selected_source(root,commit,universe):
    rows=tree(root,commit);content=blobs(root,rows);selected=set()
    for path in rows:
        p=PurePosixPath(path)
        if any(p.match(pattern) for pattern in universe["patterns"]):selected.add(path)
        if p.match(universe["fixture"]):selected.add(path)
        if path in universe["explicit"]:selected.add(path)
        if any(path.startswith("src/flywire_asca/"+leaf+"/") and path.endswith(".py") for leaf in universe["legacy_leaf_roots"]):
            selected.add(path)
    missing=set(universe["explicit"])-set(rows)
    if missing:raise ValueError("omitted required source: "+repr(sorted(missing)))
    modules={}
    for path in content:
        p=PurePosixPath(path);parts=p.with_suffix("").parts
        if parts[0]=="src":name=".".join(parts[1:])
        elif parts[0]=="scripts":name=".".join(parts)
        else:continue
        if name.endswith(".__init__"):name=name[:-9]
        modules[name]=path
        if parts[0]=="scripts":modules[p.stem]=path
    queue=list(selected);seen=set()
    def add_module(name):
        parts=name.split(".")
        for i in range(1,len(parts)+1):
            candidate=modules.get(".".join(parts[:i]))
            if candidate and candidate not in selected:selected.add(candidate);queue.append(candidate)
    while queue:
        path=queue.pop()
        if path in seen or path not in content:continue
        seen.add(path)
        p=PurePosixPath(path);parts=p.with_suffix("").parts
        package_parts=list(parts[1:] if parts[0]=="src" else parts)
        if package_parts[-1]=="__init__":package_parts.pop()
        else:package_parts.pop()
        try:parsed=ast.parse(content[path].decode("utf-8-sig"))
        except (UnicodeError,SyntaxError) as exc:raise ValueError("source parse "+path) from exc
        for node in ast.walk(parsed):
            if isinstance(node,ast.Import):
                for alias in node.names:add_module(alias.name)
            elif isinstance(node,ast.ImportFrom):
                if node.level:
                    base=package_parts[:len(package_parts)-node.level+1]
                    name=".".join(base+([node.module] if node.module else []))
                else:name=node.module or ""
                add_module(name)
                for alias in node.names:add_module(name+"."+alias.name)
        # Importing any module loads its package initializers as well.
        module_name=".".join(parts[1:-1] if parts[0]=="src" else parts[:-1]);add_module(module_name)
    return tuple(rows[p] for p in sorted(selected))
def source_fingerprint(root,commit,universe):
    root=Path(root);commit=git(root,"rev-parse",commit+"^{commit}").decode().strip()
    files=selected_source(root,commit,universe)
    head=git(root,"rev-parse","HEAD").decode().strip()
    current=selected_source(root,head,universe)
    if current!=files:raise ValueError("current behavior differs from recorded source")
    relevant={r["path"] for r in files}
    dirty=set(git(root,"diff","--name-only",commit).decode("utf-8").splitlines())
    untracked=git(root,"ls-files","--others","--exclude-standard").decode("utf-8").splitlines()
    for p in untracked:
        if (any(PurePosixPath(p).match(g) for g in universe["patterns"])
            or PurePosixPath(p).match(universe["fixture"]) or p in universe["explicit"]):dirty.add(p)
    if dirty&relevant or any(p in dirty for p in untracked):
        raise ValueError("dirty behavior source")
    return SourceFingerprint(commit,fingerprint(files),files,fingerprint(universe))
def blob_at(root,commit,path):
    return git(root,"show",commit+":"+path)
def verify_frozen_anchors(root,commit,workload):
    for ancestor in (SPEC_COMMIT,PLAN_COMMIT,G2_COMMIT):
        git(root,"merge-base","--is-ancestor",ancestor,commit)
    for name in ("public.json","requests.json","oracle.json","schemas.json","profile.json","token-bound-certificate.json","freeze.lock.json"):
        path="fixtures/a015/stage-a-v1/"+name
        if blob_at(root,commit,path)!=blob_at(root,G2_COMMIT,path):raise ValueError("G2 frozen blob changed: "+name)
    path="src/project_asca/agent_runtime/prompts.py"
    if blob_at(root,commit,path)!=blob_at(root,G2_COMMIT,path):raise ValueError("frozen role/schema source changed")
    if hashlib.sha256(blob_at(root,SPEC_COMMIT,SPEC_PATH)).hexdigest()!=SPEC_SHA256:
        raise ValueError("approved spec anchor")
    if blob_at(root,commit,SPEC_PATH)!=blob_at(root,SPEC_COMMIT,SPEC_PATH):raise ValueError("approved spec changed")
    if git(root,"rev-parse","v0.1.0").decode().strip()!="0d2b2ebd0882d2b5e950b56e227cb4a0c5de898e":raise ValueError("preserved release tag changed")
    if git(root,"rev-parse","v0.1.0^{}").decode().strip()!="fd8d298c38625b2bcfc2073fa3c8f951415a9bb2":raise ValueError("preserved release baseline changed")
