import re

import pydantic
import pytest

from aodn_collections.model.v1.physical_dataset.object_physical_dataset import (
    MissingEndAnchorError,
    MissingStartAnchorError,
    MustHaveOneCaptureGroupError,
    ObjectPhysicalDataset,
    RegexCompilationError,
)


def test_validate_patterns_accepts_valid_regexes():
    patterns = [r"^IMOS/ANMN/.*/Wave/.*\.nc$"]

    validated = ObjectPhysicalDataset.validate_patterns(patterns)

    assert validated == patterns


def test_validate_patterns_rejects_invalid_regex():
    with pytest.raises(ValueError):
        ObjectPhysicalDataset.validate_patterns(["["])


def test__compiles():
    with pytest.raises(RegexCompilationError):
        ObjectPhysicalDataset._compiles(r"[")

    assert re.compile("TEST")


def test__has_end_anchor():
    with pytest.raises(MissingEndAnchorError):
        ObjectPhysicalDataset._has_end_anchor(r"^IMOS/test.nc")

    assert ObjectPhysicalDataset._has_end_anchor(r"^IMOS/test.nc$")


def test__has_start_anchor():
    with pytest.raises(MissingStartAnchorError):
        ObjectPhysicalDataset._has_start_anchor(r"IMOS/test.nc$")

    assert ObjectPhysicalDataset._has_start_anchor(r"^IMOS/test.nc$")


def test__has_one_capture_group():
    with pytest.raises(MustHaveOneCaptureGroupError):
        ObjectPhysicalDataset._has_one_capture_group(
            r"^IMOS/SRS/SST/ghrsst/(.*/)?((?:19|20)\d{12})"
        )

    assert ObjectPhysicalDataset._has_one_capture_group(
        r"^IMOS/SRS/SST/ghrsst/(?:.*/)?((?:19|20)\d{12})"
    )


def test__validate_patterns_valid_patterns():
    patterns = [r"^IMOS/ANMN/.*/Wave/.*\.nc$"]

    validated = ObjectPhysicalDataset._validate_patterns(
        patterns=patterns,
        checks=("_compiles", "_has_start_anchor", "_has_end_anchor"),
    )

    assert validated == patterns


def test__validate_patterns_none_pattern_none_allowed():
    patterns = None

    validated = ObjectPhysicalDataset._validate_patterns(
        patterns=patterns,
        checks=("_compiles", "_has_start_anchor", "_has_end_anchor"),
    )

    assert validated == patterns


def test__validate_patterns_none_pattern_none_disallowed():
    patterns = None

    with pytest.raises(ValueError):
        ObjectPhysicalDataset._validate_patterns(
            patterns=patterns,
            checks=[],
            allow_none=False,
        )


def test__validate_patterns_todo_skipped():
    patterns = ["TODO"]

    validated = ObjectPhysicalDataset._validate_patterns(
        patterns=patterns,
        checks=("_compiles"),
    )

    assert patterns == validated


def test_patterns_validator_is_applied_during_model_validation():
    with pytest.raises(pydantic.ValidationError):
        ObjectPhysicalDataset.model_validate(
            {
                "physical_dataset_id": "physical-1",
                "type": "object",
                "patterns": ["IMOS/test.nc$"],
            }
        )
