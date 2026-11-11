import collections
import pathlib
import typing
import uuid

import polars
import pydantic
import yaml

from .collection import Collection

__YAML_SUFFIXES__ = (
    ".yml",
    ".yaml",
)
__SENTINEL_COLLECTION_METADATA_UUID__ = uuid.UUID(
    "00000000-0000-0000-0000-000000000000"
)


class Catalog(pydantic.BaseModel):
    name: str = pydantic.Field(description="The catalog name.")
    collections: list[Collection] = pydantic.Field(
        description="Collections included in the catalog."
    )

    @pydantic.model_validator(mode="after")
    def validate_unique_collection_metadata_uuids(self) -> typing.Self:
        id_counts = collections.Counter(
            collection.metadata_uuid for collection in self.collections
        )
        duplicates = sorted(
            str(metadata_uuid)
            for metadata_uuid, count in id_counts.items()
            if (count > 1 and metadata_uuid != __SENTINEL_COLLECTION_METADATA_UUID__)
        )

        if duplicates:
            raise ValueError(
                "collection metadata_uuid values must be unique within a catalog: "
                f"{', '.join(duplicates)}"
            )

        return self

    @classmethod
    def model_validate_yaml(
        cls,
        data: str | bytes | typing.IO[str] | typing.IO[bytes],
    ) -> typing.Self:
        """Parses YAML string, byte sequence, or file stream into the model."""
        parsed_dict = yaml.safe_load(data)
        assert isinstance(parsed_dict, dict), (
            "YAML data must be a key-value mapping structure."
        )
        return cls.model_validate(parsed_dict)

    @classmethod
    def from_yaml(
        cls,
        path: pathlib.Path,
    ) -> typing.Self:
        assert path.suffix in __YAML_SUFFIXES__, (
            f"file must have suffix in {__YAML_SUFFIXES__}"
        )

        with open(path) as file:
            document = yaml.safe_load(file)
            return cls.model_validate(document)

    def as_yaml(self) -> str:
        return yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False)

    @classmethod
    def from_dir(
        cls,
        catalogs_dir: pathlib.Path,
        name: str = "meta-catalog",
    ) -> typing.Self:

        # Validation
        assert catalogs_dir.is_dir(), "catalogs_dir must be a directory"
        assert all(
            path.suffix in __YAML_SUFFIXES__ for path in catalogs_dir.glob("*")
        ), "catalogs_dir must only contain yaml files"

        # Collect all the collections into a single meta catalog
        collections = []
        for catalog_path in catalogs_dir.glob("*"):
            catalog = Catalog.from_yaml(catalog_path)
            collections.extend(catalog.collections)

        return Catalog(
            name=name,
            collections=collections,
        )

    def as_table(self) -> polars.DataFrame:
        return Collection.as_table(self.collections)


if __name__ == "__main__":
    import pathlib

    catalogs_dir = pathlib.Path("catalogs/v1")
    catalog = Catalog.from_dir(catalogs_dir=catalogs_dir)
    print(catalog.as_table())
