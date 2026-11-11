import pydantic
import pytest

from aodn_collections.model.v1.logical_dataset import LogicalDataset


def test_logical_dataset_rejects_multiple_duplicate_ids_sorted():
    with pytest.raises(
        pydantic.ValidationError,
        match="physical_dataset_id values must be unique within a logical dataset: __DEFAULT__, __OPTION__",
    ):
        LogicalDataset.model_validate(
            {
                "id": "default",
                "name": "Logical A",
                "physical_datasets": [
                    {
                        "type": "object",
                        "patterns": [r"^IMOS/.+$"],
                    },
                    {
                        "id": "__OPTION__",
                        "type": "object",
                        "patterns": [r"^ANMN/.+$"],
                    },
                    {
                        "type": "object",
                        "patterns": [r"^ANMN/.+$"],
                    },
                    {
                        "id": "__OPTION__",
                        "type": "object",
                        "patterns": [r"^ANMN/.+$"],
                    },
                ],
            }
        )


def test_logical_dataset_accepts_unique_physical_dataset_ids():
    logical_dataset = LogicalDataset.model_validate(
        {
            "id": "default",
            "name": "Logical A",
            "physical_datasets": [
                {
                    "type": "object",
                    "patterns": [r"^IMOS/.+$"],
                },
                {
                    "id": "__OPTION__",
                    "type": "object",
                    "patterns": [r"^ANMN/.+$"],
                },
            ],
        }
    )

    assert len(logical_dataset.physical_datasets) == 2
