import pydantic
import pytest

from aodn_collections.model.v1.collection import (
    __NORMALISED_COLLECTION_SCHEMA__,
    Collection,
)
from aodn_collections.model.v1.logical_dataset import LogicalDataset


def test_collection_requires_at_least_one_logical_dataset():
    with pytest.raises(pydantic.ValidationError):
        Collection.model_validate(
            {
                "metadata_uuid": "00000000-0000-0000-0000-000000000001",
                "name": "Collection A",
                "logical_datasets": [],
            }
        )


def test_logical_dataset_requires_at_least_one_physical_dataset():
    with pytest.raises(pydantic.ValidationError):
        LogicalDataset.model_validate(
            {
                "id": "default",
                "name": "Logical A",
                "physical_datasets": [],
            }
        )


def test_collection_rejects_duplicate_ids():
    with pytest.raises(
        pydantic.ValidationError,
        match="id values must be unique within a collection",
    ):
        Collection.model_validate(
            {
                "metadata_uuid": "00000000-0000-0000-0000-000000000001",
                "name": "Collection A",
                "logical_datasets": [
                    {
                        "id": "default",
                        "name": "Logical A",
                        "physical_datasets": [
                            {
                                "id": "physical-1",
                                "type": "object",
                                "patterns": [r"^IMOS/.+$"],
                            }
                        ],
                    },
                    {
                        "id": "default",
                        "name": "Logical B",
                        "physical_datasets": [
                            {
                                "id": "physical-1",
                                "type": "object",
                                "patterns": [r"^IMOS/.+$"],
                            }
                        ],
                    },
                ],
            }
        )


def test_logical_dataset_rejects_duplicate_ids():
    with pytest.raises(
        pydantic.ValidationError,
        match="id values must be unique within a logical dataset",
    ):
        LogicalDataset.model_validate(
            {
                "id": "default",
                "name": "Logical A",
                "physical_datasets": [
                    {
                        "id": "physical-1",
                        "type": "object",
                        "patterns": [r"^IMOS/.+$"],
                    },
                    {
                        "id": "physical-1",
                        "type": "object",
                        "patterns": [r"^ANMN/.+$"],
                    },
                ],
            }
        )


def test_collection_accepts_unique_ids():
    collection = Collection.model_validate(
        {
            "metadata_uuid": "00000000-0000-0000-0000-000000000001",
            "name": "Collection A",
            "logical_datasets": [
                {
                    "id": "default",
                    "name": "Logical A",
                    "physical_datasets": [
                        {
                            "id": "physical-1",
                            "type": "object",
                            "patterns": [r"^IMOS/.+$"],
                        }
                    ],
                },
                {
                    "id": "derived",
                    "name": "Logical B",
                    "physical_datasets": [
                        {
                            "id": "physical-2",
                            "type": "object",
                            "patterns": [r"^ANMN/.+$"],
                        }
                    ],
                },
            ],
        }
    )

    assert len(collection.logical_datasets) == 2


def test_logical_dataset_accepts_unique_ids():
    logical_dataset = LogicalDataset.model_validate(
        {
            "id": "default",
            "name": "Logical A",
            "physical_datasets": [
                {
                    "id": "physical-1",
                    "type": "object",
                    "patterns": [r"^IMOS/.+$"],
                },
                {
                    "id": "physical-2",
                    "type": "object",
                    "patterns": [r"^ANMN/.+$"],
                },
            ],
        }
    )

    assert len(logical_dataset.physical_datasets) == 2


def test_as_table_returns_empty_dataframe_with_expected_schema():
    table = Collection.as_table([])

    assert table.is_empty()
    assert table.schema == __NORMALISED_COLLECTION_SCHEMA__


def test_as_table_normalises_nested_collection_data():
    collection = Collection.model_validate(
        {
            "metadata_uuid": "00000000-0000-0000-0000-000000000001",
            "name": "Collection A",
            "tags": ["tag-1"],
            "logical_datasets": [
                {
                    "id": "default",
                    "name": "Logical A",
                    "physical_datasets": [
                        {
                            "id": "object-1",
                            "name": "Object dataset",
                            "type": "object",
                            "patterns": [r"^IMOS/.+$"],
                        },
                        {
                            "id": "parquet-1",
                            "name": "Parquet dataset",
                            "type": "parquet",
                            "key": "path/to/dataset",
                        },
                    ],
                }
            ],
        }
    )

    rows = Collection.as_table([collection]).to_dicts()
    rows_by_physical_id = {
        row["logical_datasets.physical_datasets.id"]: row for row in rows
    }

    object_row = rows_by_physical_id["object-1"]
    assert object_row["logical_datasets.physical_datasets.type"] == "object"
    assert object_row["logical_datasets.physical_datasets.format"] == "nc"
    assert object_row["logical_datasets.physical_datasets.patterns"] == [r"^IMOS/.+$"]
    assert object_row["logical_datasets.physical_datasets.key"] is None
    assert object_row["logical_datasets.physical_datasets.store.bucket"] == "imos-data"
    assert object_row["tags"] == ["tag-1"]

    parquet_row = rows_by_physical_id["parquet-1"]
    assert parquet_row["logical_datasets.physical_datasets.type"] == "parquet"
    assert parquet_row["logical_datasets.physical_datasets.key"] == "path/to/dataset"
    assert parquet_row["logical_datasets.physical_datasets.patterns"] is None
    assert parquet_row["logical_datasets.physical_datasets.store.bucket"] == (
        "aodn-cloud-optimised"
    )


def test_as_table_adds_missing_optional_columns_as_null():
    collection = Collection.model_validate(
        {
            "metadata_uuid": "00000000-0000-0000-0000-000000000001",
            "name": "Collection A",
            "logical_datasets": [
                {
                    "id": "default",
                    "name": "Logical A",
                    "physical_datasets": [
                        {
                            "id": "object-1",
                            "type": "object",
                            "patterns": [r"^IMOS/.+$"],
                        }
                    ],
                }
            ],
        }
    )

    table = Collection.as_table([collection])
    rows = table.to_dicts()

    assert table.schema == __NORMALISED_COLLECTION_SCHEMA__
    assert rows[0]["logical_datasets.physical_datasets.key"] is None
