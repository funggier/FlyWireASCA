from __future__ import annotations

from enum import Enum


class CueKind(str, Enum):
    TEXT = "text"
    ENTITY = "entity"
    CONTEXT = "context"
    TEMPORAL = "temporal"
    PROCEDURAL = "procedural"
    OBSERVATION = "observation"


class MemoryKind(str, Enum):
    FAMILIARITY_TRACE = "familiarity_trace"
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    SPATIAL_CONTEXT = "spatial_context"
    CAUSAL_EXPLANATION = "causal_explanation"


class RelationType(str, Enum):
    SAME_PERSON = "same_person"
    SAME_NAME = "same_name"
    SIMILAR_TO = "similar_to"
    OCCURRED_AT = "occurred_at"
    OCCURRED_BEFORE = "occurred_before"
    WORKS_AT = "works_at"
    CAUSED_BY = "caused_by"
    USED_FOR = "used_for"
    PART_OF = "part_of"
    CO_OCCURS_WITH = "co_occurs_with"


class RetrievalState(str, Enum):
    UNFAMILIAR = "UNFAMILIAR"
    FAMILIAR = "FAMILIAR"
    KNOWN_BUT_NOT_RECALLED = "KNOWN_BUT_NOT_RECALLED"
    PARTIAL_RECALL = "PARTIAL_RECALL"
    RECALLED = "RECALLED"
    CONFLICTING_RECALL = "CONFLICTING_RECALL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class WorkingSetKind(str, Enum):
    MEMORY = "memory"
    PROCEDURE = "procedure"
    OBSERVATION = "observation"
    HYPOTHESIS = "hypothesis"
    GOAL = "goal"


class ObservationKind(str, Enum):
    STATE = "state"
    RESULT = "result"
    ERROR = "error"
    TOOL = "tool"
    PERCEPTION = "perception"
    EXTERNAL = "external"
