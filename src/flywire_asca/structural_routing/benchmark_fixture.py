from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from collections.abc import Iterable

from flywire_asca.contracts.validation import require_nonempty
from flywire_asca.relational_activation import (
    ActivationBenchmarkCase,
    StructuralNeed,
    build_a013_deterministic_fixture,
    shared_input_fingerprint,
)


@dataclass(frozen=True, slots=True)
class StructuralRoutingBenchmarkCase:
    routing_case_id: str
    base_a013_case_id: str
    language: str
    query_text: str
    base_case: ActivationBenchmarkCase
    expected_structural_need: StructuralNeed
    expected_target_ids: tuple[str, ...]
    expected_found: bool
    primary_relation_positive: bool

    def __post_init__(self) -> None:
        require_nonempty("routing_case_id", self.routing_case_id)
        require_nonempty("base_a013_case_id", self.base_a013_case_id)
        require_nonempty("query_text", self.query_text)
        if self.language not in ("en", "th"):
            raise ValueError('language must be "en" or "th"')
        if not isinstance(self.base_case, ActivationBenchmarkCase):
            raise ValueError("base_case must be an ActivationBenchmarkCase")
        if self.base_case.case_id != self.base_a013_case_id:
            raise ValueError("base_a013_case_id must match base_case.case_id")
        if not isinstance(self.expected_structural_need, StructuralNeed):
            raise ValueError("expected_structural_need must be a StructuralNeed")
        if any(not isinstance(value, str) or not value.strip() for value in self.expected_target_ids):
            raise ValueError("expected_target_ids must contain only nonempty strings")
        if not isinstance(self.expected_found, bool):
            raise ValueError("expected_found must be boolean")
        if not isinstance(self.primary_relation_positive, bool):
            raise ValueError("primary_relation_positive must be boolean")

    @property
    def request_id(self) -> str:
        return f"a014:{self.routing_case_id}"


@dataclass(frozen=True, slots=True)
class InvalidStructuralRoutingBenchmarkCase:
    case_id: str
    request_id: str
    query_text: str
    language_hint: str | None
    expected_error_contains: str

    def __post_init__(self) -> None:
        require_nonempty("case_id", self.case_id)
        require_nonempty("request_id", self.request_id)
        require_nonempty("expected_error_contains", self.expected_error_contains)


_QUERY_MATRIX: tuple[tuple[str, str, str], ...] = (
    ("ownership-workplace-one-hop", "Where does Ada work?", "Ada สังกัดบริษัทใด?"),
    ("causal-one-hop", "What caused the observed outage?", "ต้นตอของเหตุขัดข้องที่สังเกตพบคืออะไร?"),
    ("temporal-one-hop", "Which event happened after event Alpha?", "เหตุการณ์ถัดจาก Alpha คือเหตุการณ์ใด?"),
    ("part-of-two-hop", "Which whole system is this sensor part of?", "เซนเซอร์นี้เป็นส่วนหนึ่งของระบบใด?"),
    ("used-for-one-hop", "What is the caliper used for?", "คาลิเปอร์มีหน้าที่อะไร?"),
    ("same-name-disambiguated-ownership", "Identify this Alex's employer.", "Alex คนนี้ทำงานที่ไหน?"),
    ("cycle-control", "Which larger assembly is this component part of?", "ชิ้นส่วนนี้สังกัดชุดประกอบใด?"),
    ("low-confidence-edge-control", "What caused this observed failure?", "ต้นตอของความขัดข้องนี้คืออะไร?"),
    ("relation-allowlist-control", "What purpose does this component serve?", "ชิ้นส่วนนี้ใช้ทำอะไร?"),
    ("missing-target-control", "Who employs this person?", "บุคคลนี้ทำงานที่ไหน?"),
    ("vector-direct-control", "What fact is stated directly?", "ข้อเท็จจริงที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-context-control", "What context is stated directly?", "บริบทที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-procedure-control", "What procedure is stated directly?", "ขั้นตอนที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-causal-control", "What cause is stated directly?", "สาเหตุที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-episodic-control", "What event is stated directly?", "เหตุการณ์ที่ระบุไว้โดยตรงคืออะไร?"),
    ("vector-direct-spatial-control", "What location is stated directly?", "ตำแหน่งที่ระบุไว้โดยตรงคืออะไร?"),
)


EXPECTED_A014_CASE_IDS = (
    "ownership-workplace-one-hop:en",
    "ownership-workplace-one-hop:th",
    "causal-one-hop:en",
    "causal-one-hop:th",
    "temporal-one-hop:en",
    "temporal-one-hop:th",
    "part-of-two-hop:en",
    "part-of-two-hop:th",
    "used-for-one-hop:en",
    "used-for-one-hop:th",
    "same-name-disambiguated-ownership:en",
    "same-name-disambiguated-ownership:th",
    "cycle-control:en",
    "cycle-control:th",
    "low-confidence-edge-control:en",
    "low-confidence-edge-control:th",
    "relation-allowlist-control:en",
    "relation-allowlist-control:th",
    "missing-target-control:en",
    "missing-target-control:th",
    "vector-direct-control:en",
    "vector-direct-control:th",
    "vector-direct-context-control:en",
    "vector-direct-context-control:th",
    "vector-direct-procedure-control:en",
    "vector-direct-procedure-control:th",
    "vector-direct-causal-control:en",
    "vector-direct-causal-control:th",
    "vector-direct-episodic-control:en",
    "vector-direct-episodic-control:th",
    "vector-direct-spatial-control:en",
    "vector-direct-spatial-control:th",
)

# Populated once from the frozen fixture before policy tuning.
EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS = (('ownership-workplace-one-hop:en', '6ce7a916a7438fb5ae3a116263a28ce72c79b919c60c0d3bc027017e1532da1b'),
 ('ownership-workplace-one-hop:th', '7916a4944dc3985fee2d1c644a15013969e9ef93ddad3677139a18d30332b9d5'),
 ('causal-one-hop:en', '7fd1b0def44ffb727f5a8a88f3b9e025207816bc05154f84e5b2bc3d372336f5'),
 ('causal-one-hop:th', 'b3db781dbaa3c31b8ff43f079bc3ee455238a8cd7ca7c85e6806299d2b77c287'),
 ('temporal-one-hop:en', '7b0b5aff0dde391fd828a326c986a9edb6b1949792c7aff5d3a6cbedd464598e'),
 ('temporal-one-hop:th', '69d43b6cf18e60e767de33f9d296381f73a2e64501ceab52f518f270fea0d91d'),
 ('part-of-two-hop:en', '994eb3781d2892b243a79b725bbfe3bf201a1a32b3bfb7e9915a6d9db27a7e72'),
 ('part-of-two-hop:th', '1eff6c6180a44f0c1420242a8094b7149cd0c3a25da236c5e6e2e772db870d9e'),
 ('used-for-one-hop:en', '1f336f0683a807e9e5a92c5d5ca1611ef78472cdb2c09722e8131c719c152969'),
 ('used-for-one-hop:th', '8c4bfc8a8431c9a7e8a438e2405ed09e04bce57e4a7002d5555d2a8f1ced154e'),
 ('same-name-disambiguated-ownership:en', '5674f0e6ac526bd214275a6f96c465bc8fb9963474313931ec735cd0b5e36180'),
 ('same-name-disambiguated-ownership:th', '1e9a597374e8b99af461e314ef5f278347347ca1ec692a772b33b7c7aa3e7cf3'),
 ('cycle-control:en', 'e467a79b840d44b8e7222c151da3cf6e79e47b0fb54f2a1ef61111da6307ab0f'),
 ('cycle-control:th', '31497eb11b7b1c90fba525ab94ffe068e28d56bc34e9a4ca21da152c82bad04d'),
 ('low-confidence-edge-control:en', '28fcd223827fa73dd5cd86be2f6116a97844b3f83ef29da0b0dadc7f54777cd1'),
 ('low-confidence-edge-control:th', 'a33a5f59bf5ad38e4c9d4f90e5f51424b9a01405c8c09d5be7ce51e6bf7ad218'),
 ('relation-allowlist-control:en', 'c2e87a2d513c919485cd3d498873ff42885fe623ba9a8f60136e257aa149d203'),
 ('relation-allowlist-control:th', 'acf554e2be0c3726a4a806937d77a163fbb8e50f0bc36e872115a847adb513be'),
 ('missing-target-control:en', '07bf491ba270aefa392aa216ad481ad54ff8fd0a302f53bd58ec263554adf3d2'),
 ('missing-target-control:th', 'fd6676dad1b48257e769b9a4632a850676ef9d58ad492f6ab72301c0c6184c3f'),
 ('vector-direct-control:en', '393548841b9e9137e5c444fe735c62715229b082773eb6f97d49687f4fb9e1a5'),
 ('vector-direct-control:th', '4bb86ddbfc70160b2a5aaf0ead6117ea6935c5d1023b724e4a61aea3acb1cc31'),
 ('vector-direct-context-control:en', '5cfd592ff2c3984fe043b4ce847fb501d6718a114b95fc03b90aa0be4ad84291'),
 ('vector-direct-context-control:th', '7e7845ce30f90e26c9f746b01f65bcd5e35088e83191fb8983f9795e4e782b2e'),
 ('vector-direct-procedure-control:en', 'c7e5477e9c700d931d68ed12468222cb56adaa0870aa8261e265561fb733c832'),
 ('vector-direct-procedure-control:th', '6539d71cc2db6b05c55939692281c48cd09ab052da92254f2032e830c31d93ce'),
 ('vector-direct-causal-control:en', '3433e1c27b392a769d80e952e20f1d91f314ca0d3e8c75d843d0c1219f03d50a'),
 ('vector-direct-causal-control:th', 'b3e9e323eea0430da1e2c9c74a6a75bc984adffbcd756c89465aa5240ec22c81'),
 ('vector-direct-episodic-control:en', '07eb9132379aae5f1d01b8749bdfb4dc5bcb4fb8fc833fe6595bd243a59e0297'),
 ('vector-direct-episodic-control:th', 'd5bae9b1a718688b7b0488676ff352eef87e7d6b6cf8f0d36d5a633c2b6cd04a'),
 ('vector-direct-spatial-control:en', 'a900b1f8a22ae50f721ae30a730db944d48eb3f4fbf2ebdaa04339daa8ce9a33'),
 ('vector-direct-spatial-control:th', 'c795a594a442d0183f6d32ab8a4601c3b1f7930c2a66ec5ac9c03e3420672780'))
EXPECTED_A014_EVALUATOR_FINGERPRINTS = (('ownership-workplace-one-hop:en', '2c7593640d022d8e2c86964a2f1b85c1553b6413ecdd6e5619dc6dcddaf5975f'),
 ('ownership-workplace-one-hop:th', '5e07354588a94d4321aec826636ea0a6be9e745420554cdfc4c5602cadd7ef58'),
 ('causal-one-hop:en', '295bedd103758c576717b502f7b6ebce8c8a692a070861758b4b091654aeca16'),
 ('causal-one-hop:th', 'cce6606b81db9d873404a7335668f0a53b60d122ff8d80aff7f6a232c94859da'),
 ('temporal-one-hop:en', '2320a855a8c39c7f039e4bc1575234c92924e206d6ef4d12884bfd42894ac26d'),
 ('temporal-one-hop:th', 'c551b563bc489708443019655090a39751271b22b0c070aa2861a45dab5bafdd'),
 ('part-of-two-hop:en', 'e5cf25d6589cd5c3fcd250d20df054fc77cad4c15dff80eb0200f00354ccbe1a'),
 ('part-of-two-hop:th', '20436d6f075ef64da9dc7ae64fed87e7522a3b0b116321fe3c2570b66aeab298'),
 ('used-for-one-hop:en', 'f62833cc6b179589abea9677439eaaf675d4f2d91b0332e436bef76f8c4572f5'),
 ('used-for-one-hop:th', 'c3a6b53bf2438c017781756c79a16cf94fffb5bf0743ade1240e6730e861662b'),
 ('same-name-disambiguated-ownership:en', '48e95625331728a722b9d4370f2be22832e38bf1fbbe9bc20f850ee84031f2c4'),
 ('same-name-disambiguated-ownership:th', 'c6058ab1eac34745bdc27f4dafcc1be681359229a4b9a4ed708207ae54296882'),
 ('cycle-control:en', 'f3e238af6a7f67364ab873b13b0846e89bfac1053fadf4077e2fc9f366c0358a'),
 ('cycle-control:th', 'ae7ae008de2b9833e82703d6318139b151370660c864c8c01dd68f45058e01e0'),
 ('low-confidence-edge-control:en', '1d04eae767b427c5ec7ca71b189b7ab4fc81ce10cffbd4da58444eb6a26780e3'),
 ('low-confidence-edge-control:th', '05f46398bb1ec48d9cadafb822f4d341f1e5bc6cb41b6badcb3639c6a879f406'),
 ('relation-allowlist-control:en', '6383b46eb2e2943347ced9e8f88cede7e043bc608979121b14b8ca4218b3db77'),
 ('relation-allowlist-control:th', '7b66a2c5a4748d403e450bc3662bef4e3ac4cf9587f1e485c7a75d00c15fed96'),
 ('missing-target-control:en', 'ae6215ae23d1a2a4b8ebd8d97484e901bca5f03deafe57535df8a7745f71ee55'),
 ('missing-target-control:th', '83652a00e3997312b228e61681b4956b5a899b7bf6c4c8cdb718ba8bd4b4d854'),
 ('vector-direct-control:en', '8b4396114bfd539341fdcabd3a137b055fd322a3c7e8c04b1f28fc51114d9051'),
 ('vector-direct-control:th', '70e3d332f967604c1e11c1f54612ccc9fe8ac70688f15560ab8a7f0215650e38'),
 ('vector-direct-context-control:en', '5f55f7a892bb09b993a79ae883054fb0465098a3272c24a855589c1a64976640'),
 ('vector-direct-context-control:th', 'd583b429b6a1edb54e0720f5a95474088eb5aebff2e78e50073eada1a9d0042c'),
 ('vector-direct-procedure-control:en', '671f69d317f1d969e92e7ef5acf6ee963add72decf53811150e90eb8b67e77e8'),
 ('vector-direct-procedure-control:th', '4ea793bd1694dcd9d633d9891d87e66f35d96fcd58033841e7e231c800c9c89e'),
 ('vector-direct-causal-control:en', '9d18b16f95cde53bb9ac02ec7f17a165ab9d0db73279a4bc1f921432af72c7ac'),
 ('vector-direct-causal-control:th', 'ce305e101c26be6f3d5386f9076f3771152330933cb6caa9ac9b081b9802e18f'),
 ('vector-direct-episodic-control:en', 'e4950a6f915f1a5e3403488a3e24154a87b933a5fc41d132e1e82e2db2b0c8c5'),
 ('vector-direct-episodic-control:th', '3bb8c512238e7aea751e8a008ae755631ffb14e7acf897de88bf64d45e28ca5c'),
 ('vector-direct-spatial-control:en', 'e7ddef56fa46916a24d6bd12513c8eb6cabb66002808468e369425b5760b39a4'),
 ('vector-direct-spatial-control:th', 'e70a43452f4b15173c48ea9964d3bf6c2a788e614964e468a68761c1482b0dfb'))
EXPECTED_A014_FIXTURE_FINGERPRINT = "c100f828265063c369d535f85db8166cbeaaba26943fbb6d276a24dc46018eca"


def build_a014_frozen_fixture() -> tuple[StructuralRoutingBenchmarkCase, ...]:
    by_id = {case.case_id: case for case in build_a013_deterministic_fixture()}
    cases: list[StructuralRoutingBenchmarkCase] = []
    for base_id, english, thai in _QUERY_MATRIX:
        base = by_id[base_id]
        for language, query_text in (("en", english), ("th", thai)):
            cases.append(
                StructuralRoutingBenchmarkCase(
                    routing_case_id=f"{base_id}:{language}",
                    base_a013_case_id=base_id,
                    language=language,
                    query_text=query_text,
                    base_case=base,
                    expected_structural_need=base.structural_need,
                    expected_target_ids=base.expected_target_ids,
                    expected_found=base.expected_found,
                    primary_relation_positive=base.primary_relation_positive,
                )
            )
    return tuple(cases)


def build_a014_invalid_request_control() -> InvalidStructuralRoutingBenchmarkCase:
    return InvalidStructuralRoutingBenchmarkCase(
        case_id="invalid-request-control",
        request_id="a014:invalid-request-control",
        query_text="",
        language_hint="en",
        expected_error_contains="query_text",
    )


def _sha(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def runtime_input_fingerprint(case: StructuralRoutingBenchmarkCase) -> str:
    return _sha(
        {
            "request_id": case.request_id,
            "query_text": case.query_text,
            "language_hint": case.language,
        }
    )


def evaluator_metadata_fingerprint(case: StructuralRoutingBenchmarkCase) -> str:
    return _sha(
        {
            "routing_case_id": case.routing_case_id,
            "base_a013_case_id": case.base_a013_case_id,
            "base_a013_shared_input_fingerprint": shared_input_fingerprint(case.base_case),
            "expected_structural_need": {
                "required_relations": tuple(
                    relation.value
                    for relation in case.expected_structural_need.required_relations
                ),
                "requires_path_provenance": (
                    case.expected_structural_need.requires_path_provenance
                ),
            },
            "expected_target_ids": case.expected_target_ids,
            "expected_found": case.expected_found,
            "primary_relation_positive": case.primary_relation_positive,
        }
    )


def _invalid_control_payload() -> dict[str, object]:
    invalid = build_a014_invalid_request_control()
    return {
        "case_id": invalid.case_id,
        "request_id": invalid.request_id,
        "query_text": invalid.query_text,
        "language_hint": invalid.language_hint,
        "expected_error_contains": invalid.expected_error_contains,
    }


def a014_fixture_fingerprint(
    cases: Iterable[StructuralRoutingBenchmarkCase],
) -> str:
    materialized = tuple(cases)
    return _sha(
        {
            "cases": [
                {
                    "routing_case_id": case.routing_case_id,
                    "runtime_input_fingerprint": runtime_input_fingerprint(case),
                    "evaluator_metadata_fingerprint": evaluator_metadata_fingerprint(case),
                }
                for case in materialized
            ],
            "invalid_request_control": _invalid_control_payload(),
        }
    )
