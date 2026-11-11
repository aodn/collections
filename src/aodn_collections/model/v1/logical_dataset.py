import collections
import typing

import pydantic

from .physical_dataset import PhysicalDataset


class LogicalDataset(pydantic.BaseModel):
    id: str = pydantic.Field(
        default="__DEFAULT__",
        description="Stable identifier unique within a collection.",
    )
    name: str | None = pydantic.Field(
        default=None,
        description="Human-readable logical dataset name.",
    )
    physical_datasets: list[PhysicalDataset] = pydantic.Field(
        min_length=1,
        description="Physical datasets available for this logical dataset.",
    )

    @pydantic.model_validator(mode="after")
    def validate_unique_physical_dataset_ids(self) -> typing.Self:
        id_counts = collections.Counter(
            dataset.id for dataset in self.physical_datasets
        )
        duplicates = sorted(
            physical_dataset_id
            for physical_dataset_id, count in id_counts.items()
            if count > 1
        )

        if duplicates:
            raise ValueError(
                "physical_dataset_id values must be unique within a logical dataset: "
                f"{', '.join(duplicates)}"
            )

        return self
