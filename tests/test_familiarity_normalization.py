from __future__ import annotations

import pytest

from flywire_asca.contracts import CueKind
from flywire_asca.familiarity import familiarity_key, normalize_surface


def test_normalize_surface_uses_nfkc_whitespace_collapse_and_casefold():
    assert normalize_surface("  Alice  ") == "alice"
    assert normalize_surface("ＡＬＩＣＥ") == "alice"
    assert normalize_surface("สวัสดี\u00a0  โลก") == "สวัสดี โลก"


def test_normalize_surface_rejects_empty_after_normalization():
    with pytest.raises(ValueError, match="surface_value"):
        normalize_surface(" \t\r\n ")


def test_familiarity_key_keeps_cue_kind_separate():
    entity = familiarity_key(CueKind.ENTITY, " A ")
    text = familiarity_key(CueKind.TEXT, " A ")
    assert entity == (CueKind.ENTITY, "a")
    assert text == (CueKind.TEXT, "a")
    assert entity != text


def test_normalization_is_deterministic():
    value = "  Café\u00a0TEST "
    assert normalize_surface(value) == normalize_surface(value)
    assert familiarity_key(CueKind.CONTEXT, value) == familiarity_key(CueKind.CONTEXT, value)
