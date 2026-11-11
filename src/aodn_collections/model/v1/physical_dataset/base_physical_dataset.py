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
    time_coverage_field_name: str | None = pydantic.Field(default=None)
    geospatial_lat_field_name: str | None = pydantic.Field(default=None)
    geospatial_lon_field_name: str | None = pydantic.Field(default=None)
