import re
import typing

import pydantic

from aodn_collections.model.v1.store import S3Store

from .base_physical_dataset import BasePhysicalDataset

FORMAT = typing.Literal[
    "nc",
    "csv",
]


class ObjectPhysicalDataset(BasePhysicalDataset):
    type: typing.Literal["object"] = pydantic.Field(
        description="Physical dataset type discriminator."
    )
    format: FORMAT = pydantic.Field(
        default="nc",
        description="Object dataset file format.",
    )
    store: S3Store = pydantic.Field(
        default_factory=lambda: S3Store(),
        description="S3 storage location for the object dataset.",
    )
    patterns: list[str] = pydantic.Field(
        description="Regex patterns used to match dataset objects."
    )

    @property
    def unified_pattern(self) -> str:
        return "|".join(self.patterns)

    @staticmethod
    def _compiles(pattern: str):
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"patterns must be valid regex: got `{pattern}`: {e}")
        return True

    @staticmethod
    def _has_start_anchor(pattern: str):
        if not pattern.startswith("^"):
            raise ValueError(
                f"patterns must have a start anchor (`^`): got `{pattern}`"
            )
        return True

    @staticmethod
    def _has_end_anchor(pattern: str):
        if not pattern.endswith("$"):
            raise ValueError(f"patterns must have an end anchor (`$`): got `{pattern}`")
        return True

    @pydantic.field_validator("patterns")
    @classmethod
    def validate_patterns(cls, patterns: list[str]) -> list[str]:
        for pattern in [pattern for pattern in patterns if pattern != "TODO"]:
            cls._compiles(pattern)
            cls._has_start_anchor(pattern)
            cls._has_end_anchor(pattern)

        return patterns
