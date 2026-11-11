import pathlib

import pydantic
import pytest

from aodn_collections import CATALOGS_V1_DIR
from aodn_collections.model.v1 import Catalog
from aodn_collections.model.v1.collection import Collection

CATALOGS_DIR = CATALOGS_V1_DIR
CATALOG_PATHS = sorted(CATALOGS_DIR.glob("*.yaml"))


@pytest.mark.parametrize("catalog_path", CATALOG_PATHS, ids=lambda path: path.name)
def test_catalog_yaml_files_validate(catalog_path: pathlib.Path):
    catalog = Catalog.from_yaml(catalog_path)

    assert isinstance(catalog, Catalog)


def test_from_yaml_rejects_non_yaml_suffix(tmp_path: pathlib.Path):
    path = tmp_path / "catalog.json"
    path.write_text("name: invalid\ncollections: []\n")

    with pytest.raises(AssertionError, match="file must have suffix in"):
        Catalog.from_yaml(path)


def test_from_dir_merges_collections_from_yaml_files(tmp_path: pathlib.Path):
    selected_paths = CATALOG_PATHS[:2]
    for path in selected_paths:
        (tmp_path / path.name).write_text(path.read_text())

    meta_catalog = Catalog.from_dir(tmp_path, name="merged")
    expected_collection_count = sum(
        len(Catalog.from_yaml(path).collections) for path in selected_paths
    )

    assert meta_catalog.name == "merged"
    assert len(meta_catalog.collections) == expected_collection_count


def test_from_dir_requires_directory(tmp_path: pathlib.Path):
    path = tmp_path / "catalog.yaml"
    path.write_text("name: invalid\ncollections: []\n")

    with pytest.raises(AssertionError, match="catalogs_dir must be a directory"):
        Catalog.from_dir(path, name="merged")


def test_from_dir_rejects_non_yaml_files(tmp_path: pathlib.Path):
    (tmp_path / "notes.txt").write_text("not yaml")

    with pytest.raises(
        AssertionError, match="catalogs_dir must only contain yaml files"
    ):
        Catalog.from_dir(tmp_path, name="merged")


def test_catalog_rejects_duplicate_collection_metadata_uuids():
    with pytest.raises(
        pydantic.ValidationError,
        match=(
            "collection metadata_uuid values must be unique within a catalog: "
            "00000000-0000-0000-0000-000000000001"
        ),
    ):
        Catalog.model_validate(
            {
                "name": "catalog",
                "collections": [
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
                    },
                    {
                        "metadata_uuid": "00000000-0000-0000-0000-000000000001",
                        "name": "Collection B",
                        "logical_datasets": [
                            {
                                "id": "derived",
                                "name": "Logical B",
                                "physical_datasets": [
                                    {
                                        "id": "object-2",
                                        "type": "object",
                                        "patterns": [r"^ANMN/.+$"],
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        )


def test_catalog_accepts_unique_collection_metadata_uuids():
    catalog = Catalog.model_validate(
        {
            "name": "catalog",
            "collections": [
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
                },
                {
                    "metadata_uuid": "00000000-0000-0000-0000-000000000002",
                    "name": "Collection B",
                    "logical_datasets": [
                        {
                            "id": "derived",
                            "name": "Logical B",
                            "physical_datasets": [
                                {
                                    "id": "object-2",
                                    "type": "object",
                                    "patterns": [r"^ANMN/.+$"],
                                }
                            ],
                        }
                    ],
                },
            ],
        }
    )

    assert len(catalog.collections) == 2


def test_catalog_allows_duplicate_sentinel_collection_metadata_uuid():
    catalog = Catalog.model_validate(
        {
            "name": "catalog",
            "collections": [
                {
                    "metadata_uuid": "00000000-0000-0000-0000-000000000000",
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
                },
                {
                    "metadata_uuid": "00000000-0000-0000-0000-000000000000",
                    "name": "Collection B",
                    "logical_datasets": [
                        {
                            "id": "derived",
                            "name": "Logical B",
                            "physical_datasets": [
                                {
                                    "id": "object-2",
                                    "type": "object",
                                    "patterns": [r"^ANMN/.+$"],
                                }
                            ],
                        }
                    ],
                },
            ],
        }
    )

    assert len(catalog.collections) == 2


def test_catalog_as_table_matches_collection_as_table():
    catalog = Catalog.model_validate(
        {
            "name": "catalog",
            "collections": [
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
                                    "name": "Object dataset",
                                    "type": "object",
                                    "patterns": [r"^IMOS/.+$"],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )

    assert (
        catalog.as_table().to_dicts()
        == Collection.as_table(catalog.collections).to_dicts()
    )
