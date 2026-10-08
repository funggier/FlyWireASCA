from __future__ import annotations

import unicodedata

from flywire_asca.contracts import CueKind


def normalize_surface(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    collapsed = " ".join(normalized.split()).casefold()
    if not collapsed:
        raise ValueError("surface_value must not be empty after normalization")
    return collapsed


def familiarity_key(kind: CueKind, surface_value: str) -> tuple[CueKind, str]:
    return (kind, normalize_surface(surface_value))
