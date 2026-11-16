import pydantic
import pytest

from aodn_collections.model.v1.physical_dataset.object_physical_dataset import (
    ObjectPhysicalDataset,
)


def _as_pattern_list(patterns: str | None) -> list[str] | None:
    if patterns is None:
        return None
    return [patterns]


@pytest.mark.parametrize(
    "patterns",
    [
        # All valid patterns
        # All have start and end anchors
        r"^IMOS/ANMN/.*/Wave/.*\.nc$",
        r"^IMOS/.*\.nc$",
        r"^IMOS/.*\.csv$",
        "TODO",
    ],
)
def test_patterns_accept_valid_values_during_model_validation(patterns):
    normalized_patterns = _as_pattern_list(patterns)
    dataset = ObjectPhysicalDataset.model_validate(
        {"type": "object", "patterns": normalized_patterns}
    )
    assert dataset.patterns == normalized_patterns


@pytest.mark.parametrize(
    "patterns",
    [
        # Invalid pattern
        "[",
        # Missing start anchor
        r"IMOS/test\.nc$",
        # Missing end anchor
        r"^IMOS/test\.nc",
    ],
)
def test_patterns_reject_invalid_values_during_model_validation(patterns):
    with pytest.raises(pydantic.ValidationError):
        ObjectPhysicalDataset.model_validate(
            {"type": "object", "patterns": _as_pattern_list(patterns)}
        )


@pytest.mark.parametrize("field", ["start_date_patterns", "end_date_patterns"])
@pytest.mark.parametrize(
    "patterns",
    [
        # None allowed
        None,
        # Has one capture group
        r"^IMOS/(\d{14})$",
        # Has one named capture group
        r"^IMOS/(?P<timestamp>\d{14})$",
        # Has one ignore capture group and one capture group
        r"^IMOS/(?:.*/)?(\d{14})$",
    ],
)
def test_date_patterns_accept_valid_values_during_model_validation(field, patterns):
    normalized_patterns = _as_pattern_list(patterns)
    required_patterns = _as_pattern_list(r"^IMOS/.*\.nc$")
    dataset = ObjectPhysicalDataset.model_validate(
        {"type": "object", "patterns": required_patterns, field: normalized_patterns}
    )
    assert getattr(dataset, field) == normalized_patterns


@pytest.mark.parametrize("field", ["start_date_patterns", "end_date_patterns"])
@pytest.mark.parametrize(
    "patterns",
    [
        # Invalid
        "[",
        # Has no capture group
        r"^IMOS/\d{14}$",
        # Has one ignore capture group
        r"^IMOS/(?:\d{14})$",
        # Has two capture groups
        r"^IMOS/(\d{8})(\d{6})$",
    ],
)
def test_date_patterns_reject_invalid_values_during_model_validation(field, patterns):
    required_patterns = _as_pattern_list(r"^IMOS/.*\.nc$")
    with pytest.raises(pydantic.ValidationError):
        ObjectPhysicalDataset.model_validate(
            {
                "type": "object",
                "patterns": required_patterns,
                field: _as_pattern_list(patterns),
            }
        )
