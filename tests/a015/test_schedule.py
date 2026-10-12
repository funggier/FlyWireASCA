from collections import Counter
import pytest
def test_fixed_schedule_has_384_balanced_slots(workload):
    from project_asca.evaluation.schedule import trial_schedule
    slots=trial_schedule(workload)
    assert len(slots)==384
    assert Counter((s.case.case_id,s.variant.value) for s in slots)=={
        (c.case_id,v):3 for c in workload.cases for v in ("UNIFIED_RUNTIME","DIRECT_PINNED_MODEL")}
    pairs=list(dict.fromkeys(c.pair_id for c in workload.cases))
    for r in (1,2,3):
        batch=[s for s in slots if s.repetition==r]
        assert [s.case.case_id for s in batch[::2]]==[c.case_id for c in workload.cases]
        for i,pair in enumerate(pairs):
            group=[s for s in batch if s.case.pair_id==pair]
            assert [s.case.language for s in group]==["en","en","th","th"]
            first="UNIFIED_RUNTIME" if (i+r-1)%2==0 else "DIRECT_PINNED_MODEL"
            assert group[0].variant.value==group[2].variant.value==first
def test_protocol_cannot_silently_lower_repetitions_or_change_seed(workload):
    from project_asca.evaluation.schedule import trial_schedule
    for kw in ({"repetitions":2},{"repetitions":True},{"seed":1}):
        with pytest.raises(ValueError):trial_schedule(workload,**kw)
