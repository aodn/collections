import typing

import pydantic

from aodn_collections.model.v1.store import S3Store

from .base_physical_dataset import BasePhysicalDataset


class CloudOptimisedPhysicalDataset(BasePhysicalDataset):
    type: typing.Literal["parquet", "zarr"] = pydantic.Field(
        description="Cloud-optimised physical dataset type discriminator."
    )
    store: S3Store = pydantic.Field(
        default_factory=lambda: S3Store(
            type="s3",
            bucket="aodn-cloud-optimised",
            region="ap-southeast-2",
        ),
        description="S3 storage location for cloud-optimised datasets.",
    )
    key: str = pydantic.Field(
        description="The cloud storage directory of the cloud-optimised dataset."
    )
