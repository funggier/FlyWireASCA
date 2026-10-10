import pytest

from flywire_asca.contracts import validation


class MarkerError(Exception):
    pass


def helper(name: str):
    assert hasattr(validation, name), f"validation.{name} must exist"
    return getattr(validation, name)


def test_shared_json_shape_validator_api_exists():
    for name in (
        "require_mapping",
        "require_list",
        "require_string",
        "optional_string",
        "optional_nonnegative_int",
    ):
        assert hasattr(validation, name), name


def test_shared_json_shape_validators_pass_valid_values_through():
    require_mapping = helper("require_mapping")
    require_list = helper("require_list")
    require_string = helper("require_string")
    optional_string = helper("optional_string")
    optional_nonnegative_int = helper("optional_nonnegative_int")
    mapping = {"a": 1}
    array = ["x"]
    assert require_mapping("field", mapping) is mapping
    assert require_list("field", array) is array
    assert require_string("field", "value") == "value"
    assert optional_string("field", None) is None
    assert optional_string("field", "value") == "value"
    assert optional_nonnegative_int("field", None) is None
    assert optional_nonnegative_int("field", 0) == 0
    assert optional_nonnegative_int("field", 4) == 4


@pytest.mark.parametrize(
    ("helper_name", "value", "message"),
    (
        ("require_mapping", [], "field must be an object"),
        ("require_list", {}, "field must be an array"),
        ("require_string", " ", "field must be a nonblank string"),
        ("optional_nonnegative_int", True, "field must be a nonnegative integer"),
        ("optional_nonnegative_int", -1, "field must be a nonnegative integer"),
    ),
)
def test_shared_json_shape_validators_raise_caller_selected_error_type(
    helper_name, value, message
):
    function = helper(helper_name)
    with pytest.raises(MarkerError, match=message):
        function("field", value, error_type=MarkerError)
