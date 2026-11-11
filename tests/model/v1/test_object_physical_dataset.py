import re

import pydantic
import pytest

from aodn_collections.model.v1.physical_dataset.object_physical_dataset import (
    ObjectPhysicalDataset,
)


def test_validate_patterns_accepts_valid_regexes():
    patterns = [r"^IMOS/ANMN/.*/Wave/.*\.nc$"]

    validated = ObjectPhysicalDataset.validate_patterns(patterns)

    assert validated == patterns


def test_validate_patterns_allows_todo_placeholder():
    patterns = ["TODO"]

    validated = ObjectPhysicalDataset.validate_patterns(patterns)

    assert validated == patterns


def test_validate_patterns_rejects_invalid_regex():
    with pytest.raises(ValueError):
        ObjectPhysicalDataset.validate_patterns(["["])


def test__compiles():
    with pytest.raises(ValueError):
        ObjectPhysicalDataset._compiles(r"[")

    assert re.compile("TEST")


def test__has_end_anchor():
    with pytest.raises(ValueError):
        ObjectPhysicalDataset._has_end_anchor("^IMOS/test.nc")

    assert ObjectPhysicalDataset._has_end_anchor("^IMOS/test.nc$")


def test__has_start_anchor():
    with pytest.raises(ValueError):
        ObjectPhysicalDataset._has_start_anchor("IMOS/test.nc$")

    assert ObjectPhysicalDataset._has_start_anchor("^IMOS/test.nc$")


def test_patterns_validator_is_applied_during_model_validation():
    with pytest.raises(pydantic.ValidationError):
        ObjectPhysicalDataset.model_validate(
            {
                "physical_dataset_id": "physical-1",
                "type": "object",
                "patterns": ["IMOS/test.nc$"],
            }
        )
