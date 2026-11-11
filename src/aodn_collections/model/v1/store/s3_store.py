import typing

import pydantic


class S3Store(pydantic.BaseModel):
    type: typing.Literal["s3"] = pydantic.Field(
        default="s3",
        description="Storage provider type.",
    )
    bucket: str = pydantic.Field(
        default="imos-data",
        description="S3 bucket name.",
    )
    region: str = pydantic.Field(
        default="ap-southeast-2",
        description="AWS region where the bucket is hosted.",
    )
