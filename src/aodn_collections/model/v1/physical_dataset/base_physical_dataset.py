import pydantic


class BasePhysicalDataset(pydantic.BaseModel):
    id: str = pydantic.Field(
        default="__DEFAULT__",
        description="Stable identifier unique within the parent logical dataset.",
    )
    name: str | None = pydantic.Field(
        default=None,
        description="Optional human-readable physical dataset name.",
    )
