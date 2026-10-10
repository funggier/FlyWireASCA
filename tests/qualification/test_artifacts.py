from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pytest
from flywire_asca.qualification.artifacts import ArtifactStore, artifact_issues, publish_pack, render_pack_markdown
from flywire_asca.qualification.manifest import decode_pack, manifest_issues
from flywire_asca.qualification.profile import DEFAULT_PROFILE_PATH, load_frozen_profile
from flywire_asca.qualification.records import ArtifactRecord, QualificationError, Scope

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def stored_pack(tmp_path, make_pack):
    def build(scope=Scope.FULL_SYSTEM):
        store = ArtifactStore.create(ROOT, tmp_path / ("full" if scope == Scope.FULL_SYSTEM else "portable"))
        pack = make_pack(scope)
        raw = (ROOT/DEFAULT_PROFILE_PATH).read_bytes()
        profile = load_frozen_profile(raw)
        store.write_raw("profile.json",raw,"profile")
        for record in pack.artifact_index:
            store.write_raw(record.path,b"{}","gate")
        snapshots = {key:replace(getattr(pack.source,key),profile_sha256=profile.sha256,protected_sha256=profile.values["protected_source"]["sha256"]) for key in ("before","after")}
        pack = replace(pack,profile=replace(pack.profile,sha256=profile.sha256,expected_sha256=profile.sha256),
            source=replace(pack.source,protected_sha256=profile.values["protected_source"]["sha256"],**snapshots),
            replay_identity=replace(pack.replay_identity,profile_sha256=profile.sha256,
                observations=tuple(replace(o,profile_sha256=profile.sha256) for o in pack.replay_identity.observations)),
            artifact_index=store.index())
        return store,pack
    return build


@pytest.mark.parametrize("mutation", ["missing","hash","length"])
def test_missing_raw_file_or_hash_length_mismatch_fails(stored_pack, mutation):
    store,pack = stored_pack()
    entry = next(a for a in pack.artifact_index if a.kind == "gate")
    path = store.root/entry.path
    if mutation == "missing":
        path.unlink()
    elif mutation == "hash":
        path.write_bytes(b"[]")
    else:
        path.write_bytes(b"{} extra")
    assert artifact_issues(pack,store.root)
    with pytest.raises(QualificationError):
        publish_pack(store,pack)


def test_manifest_refs_resolve_to_indexed_relative_files(stored_pack):
    store,pack = stored_pack()
    gate = replace(pack.gates[0],artifacts=("../outside.json",))
    pack = replace(pack,gates=(gate,)+pack.gates[1:])
    assert artifact_issues(pack,store.root)
    with pytest.raises(QualificationError):
        publish_pack(store,pack)


def test_index_never_hashes_itself_manifest_or_report(stored_pack):
    store,pack = stored_pack()
    manifest,report = publish_pack(store,pack)
    assert manifest.exists() and report.exists() and (store.root/"artifact-index.json").exists()
    assert all(a.path not in {"qualification.json","qualification.md","artifact-index.json"} for a in store.index())
    assert decode_pack(manifest.read_bytes()) == pack
    assert json.loads((store.root/"artifact-index.json").read_bytes()) == json.loads(manifest.read_bytes())["artifact_index"]


@pytest.mark.parametrize("mutation", ["profile","candidate"])
def test_source_profile_or_candidate_mix_fails(stored_pack, mutation):
    store,pack = stored_pack()
    if mutation == "profile":
        pack = replace(pack,profile=replace(pack.profile,sha256="d"*64))
    else:
        pack = replace(pack,source=replace(pack.source,commit="d"*40))
    assert artifact_issues(pack,store.root)
    with pytest.raises(QualificationError):
        publish_pack(store,pack)


def test_existing_directory_or_inside_checkout_is_refused(tmp_path):
    root = tmp_path/"repo"
    root.mkdir()
    original_path = tmp_path/"existing"/"previous.bin"
    original_path.parent.mkdir()
    original_path.write_bytes(b"preserve")
    original_bytes = original_path.read_bytes()
    for output in (original_path.parent,root/"pack"):
        with pytest.raises(QualificationError):
            ArtifactStore.create(root,output)
    assert original_path.read_bytes() == original_bytes
    assert not (root/"pack").exists()


@pytest.mark.parametrize("relative", ["../escape","/absolute","C:/escape","a/../escape","a\\escape","qualification.json","artifact-index.json"])
def test_link_and_parent_path_escape_is_rejected(tmp_path, relative):
    store = ArtifactStore.create(tmp_path/"repo",tmp_path/"pack")
    with pytest.raises(QualificationError):
        store.write_raw(relative,b"data","raw")


def test_symlink_or_junction_ancestor_is_refused(tmp_path):
    repo = tmp_path/"repo"
    target = tmp_path/"target"
    target.mkdir()
    link = tmp_path/"link"
    try:
        link.symlink_to(target,target_is_directory=True)
    except OSError:
        if os.name != "nt":
            pytest.skip("filesystem does not support symlinks")
        result = subprocess.run(["cmd","/d","/c","mklink","/J",str(link),str(target)],capture_output=True)
        assert result.returncode == 0, result.stderr
    with pytest.raises(QualificationError):
        ArtifactStore.create(repo,link/"pack")
    assert not (target/"pack").exists()


def test_hardlink_and_replaced_root_are_rejected(stored_pack, tmp_path):
    store,pack = stored_pack()
    entry = next(a for a in pack.artifact_index if a.kind == "gate")
    alias = tmp_path/"alias"
    os.link(store.root/entry.path,alias)
    assert artifact_issues(pack,store.root)
    with pytest.raises(QualificationError):
        publish_pack(store,pack)


def test_write_failure_never_returns_passing_publication(stored_pack, monkeypatch):
    store,pack = stored_pack()
    def fail(*args,**kwargs):
        raise OSError("injected atomic replace failure")
    monkeypatch.setattr(os,"replace",fail)
    with pytest.raises(QualificationError) as exc:
        publish_pack(store,pack)
    assert exc.value.code == "ARTIFACT_WRITE_FAILED"
    assert not (store.root/"qualification.md").exists() or not (store.root/"qualification.md").read_bytes()


def test_report_is_derived_from_validated_manifest(stored_pack):
    store,pack = stored_pack(Scope.PORTABLE_ONLY)
    report = render_pack_markdown(pack)
    assert "PORTABLE_ONLY" in report and "is_final=false" in report and "engineering_verdict=null" in report
    for milestone in ("A006","A007","A008","A009","A010"):
        assert milestone in report
    assert "ASCA intelligence score" not in report
    bad = replace(pack,is_final=True)
    with pytest.raises(QualificationError):
        render_pack_markdown(bad)


def test_raw_file_is_never_overwritten(tmp_path):
    store = ArtifactStore.create(tmp_path/"repo",tmp_path/"pack")
    store.write_raw("raw.bin",b"first","raw")
    with pytest.raises(QualificationError):
        store.write_raw("raw.bin",b"second","raw")
    assert (store.root/"raw.bin").read_bytes() == b"first"


def test_manifest_cannot_index_its_own_index(make_pack):
    pack = make_pack()
    extra = ArtifactRecord("artifact-index.json","raw",hashlib.sha256(b"{}").hexdigest(),2)
    assert manifest_issues(replace(pack,artifact_index=pack.artifact_index+(extra,)))


def test_profile_drift_failure_pack_retains_diagnostic_copy(stored_pack, tmp_path):
    from flywire_asca.qualification.records import GateStatus, Reason, FrozenCheck
    from flywire_asca.qualification.classifier import classify_full, classify_portable, pack_exit_code
    old,pack = stored_pack()
    store = ArtifactStore.create(ROOT,tmp_path/"failed-profile")
    bad = b"{\"changed_profile\":true}"
    observed_hash = hashlib.sha256(bad).hexdigest()
    for entry in old.index():
        store.write_raw(entry.path,bad if entry.kind == "profile" else (old.root/entry.path).read_bytes(),entry.kind)
    reason = Reason("PROFILE_DRIFT","P00_PROFILE_SOURCE","Captured profile bytes differ from literal anchor",("profile.json",))
    gates = tuple(replace(g,status=GateStatus.FAIL,exit_code=1,errors=(reason,)) if g.gate_id == "P00_PROFILE_SOURCE"
        else replace(g,status=GateStatus.NOT_RUN,command=None,started_at=None,finished_at=None,
            exit_code=None,artifacts=(),errors=(),cause_ids=("P00_PROFILE_SOURCE",)) for g in pack.gates)
    pack = replace(pack,profile=replace(pack.profile,sha256=observed_hash),
        source=replace(pack.source,before=replace(pack.source.before,profile_sha256=observed_hash,clean=False),
                                   after=replace(pack.source.after,profile_sha256=observed_hash,clean=False)),
        gates=gates,errors=(reason,),portable_status=classify_portable(gates,(reason,),()),
        engineering_verdict=classify_full(gates,(reason,),()),physical_environment=None,
        research_evidence=tuple(replace(r,observations=()) for r in pack.research_evidence),
        replay_identity=replace(pack.replay_identity,profile_sha256=observed_hash,observations=()),
        frozen_checks=(FrozenCheck("profile.sha256",pack.profile.expected_sha256,observed_hash,GateStatus.FAIL,("profile.json",)),),
        artifact_index=store.index())
    assert manifest_issues(pack) == ()
    assert artifact_issues(pack,store.root) == ()
    manifest,report = publish_pack(store,pack)
    assert decode_pack(manifest.read_bytes()) == pack and pack_exit_code(pack) == 1
