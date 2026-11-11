import collections
import typing
import uuid

import polars
import pydantic

from .logical_dataset import LogicalDataset

__NORMALISED_COLLECTION_SCHEMA__ = polars.Schema(
    {
        "metadata_uuid": polars.String,
        "name": polars.String,
        "logical_datasets.id": polars.String,
        "logical_datasets.name": polars.String,
        "logical_datasets.physical_datasets.id": polars.String,
        "logical_datasets.physical_datasets.name": polars.String,
        "logical_datasets.physical_datasets.type": polars.String,
        "logical_datasets.physical_datasets.format": polars.String,
        "logical_datasets.physical_datasets.store.type": polars.String,
        "logical_datasets.physical_datasets.store.bucket": polars.String,
        "logical_datasets.physical_datasets.store.region": polars.String,
        "logical_datasets.physical_datasets.patterns": polars.List(polars.String),
        "logical_datasets.physical_datasets.key": polars.String,
        "tags": polars.List(polars.String),
    }
)


class Collection(pydantic.BaseModel):
    metadata_uuid: uuid.UUID = pydantic.Field(
        validation_alias=pydantic.AliasChoices("metadata_uuid", "uuid"),
        description="Stable metadata UUID for the collection.",
    )
    name: str = pydantic.Field(description="Human-readable collection name.")
    logical_datasets: list[LogicalDataset] = pydantic.Field(
        min_length=1,
        description="Logical datasets that belong to this collection.",
    )
    tags: list[str] = pydantic.Field(
        default=[],
        description="Optional tags associated with the collection.",
    )

    @pydantic.field_serializer("metadata_uuid")
    def serialize_metadata_uuid(self, value: uuid.UUID) -> str:
        return str(value)

    @pydantic.model_validator(mode="after")
    def validate_unique_logical_dataset_ids(self) -> typing.Self:
        id_counts = collections.Counter(dataset.id for dataset in self.logical_datasets)
        duplicates = sorted(
            logical_dataset_id
            for logical_dataset_id, count in id_counts.items()
            if count > 1
        )

        if duplicates:
            raise ValueError(
                "logical_dataset_id values must be unique within a collection: "
                f"{', '.join(duplicates)}"
            )

        return self

    @classmethod
    def as_table(cls, collections: list[typing.Self]) -> polars.DataFrame:

        if not collections:
            return polars.DataFrame(schema=__NORMALISED_COLLECTION_SCHEMA__)

        df = (
            polars.json_normalize(
                (collection.model_dump() for collection in collections),
                strict=False,
            )
            .explode("logical_datasets")
            .unnest(
                "logical_datasets",
                separator=".",
            )
            .explode("logical_datasets.physical_datasets")
            .unnest(
                "logical_datasets.physical_datasets",
                separator=".",
            )
            .unnest(
                "logical_datasets.physical_datasets.store",
                separator=".",
            )
        )

        missing_column_exprs = [
            polars.lit(None, dtype=dtype).alias(column)
            for column, dtype in __NORMALISED_COLLECTION_SCHEMA__.items()
            if column not in df.columns
        ]
        if missing_column_exprs:
            df = df.with_columns(missing_column_exprs)

        # Re-Order and cast
        df = df.select(__NORMALISED_COLLECTION_SCHEMA__.names()).cast(
            dtypes=__NORMALISED_COLLECTION_SCHEMA__,
            strict=True,
        )

        return df
