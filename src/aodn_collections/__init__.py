"""collection_object_mapping package."""

import pathlib

from aodn_collections.model.v1.catalog import Catalog

CATALOGS_V1_DIR: pathlib.Path = (
    pathlib.Path(__file__).resolve().parent / "catalogs" / "v1"
).absolute()


CATALOG_V1: Catalog = Catalog.from_dir(CATALOGS_V1_DIR)

__all__ = [
    "CATALOGS_V1_DIR",
    "CATALOG_V1",
]
