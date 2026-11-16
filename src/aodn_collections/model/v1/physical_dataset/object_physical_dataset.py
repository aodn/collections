import re
import typing

import pydantic

from aodn_collections.model.v1.store import S3Store

from .base_physical_dataset import BasePhysicalDataset

__FORMAT__ = typing.Literal[
    "nc",
    "csv",
]

__PATTERN_VALIDATION_METHODS__ = typing.Literal[
    "_compiles",
    "_has_start_anchor",
    "_has_end_anchor",
]


class RegexCompilationError(ValueError): ...


class MissingStartAnchorError(ValueError): ...


class MissingEndAnchorError(ValueError): ...


class ObjectPhysicalDataset(BasePhysicalDataset):
    type: typing.Literal["object"] = pydantic.Field(
        description="Physical dataset type discriminator."
    )
    format: __FORMAT__ = pydantic.Field(
        default="nc",
        description="Object dataset file format.",
    )
    store: S3Store = pydantic.Field(
        default_factory=lambda: S3Store(),
        description="S3 storage location for the object dataset.",
    )
    patterns: typing.Sequence[str] = pydantic.Field(
        description="Regex patterns used to match dataset objects."
    )
    start_date_patterns: typing.Sequence[str] | None = pydantic.Field(default=None)
    end_date_patterns: typing.Sequence[str] | None = pydantic.Field(default=None)

    def unified_pattern(self, attribute: str = "patterns") -> str:
        return "|".join(getattr(self, attribute))

    @staticmethod
    def _compiles(pattern: str) -> typing.Literal[True]:
        try:
            re.compile(pattern)
        except re.error as e:
            raise RegexCompilationError(
                f"patterns must be valid regex: got `{pattern}`: {e}"
            )

        return True

    @staticmethod
    def _has_start_anchor(pattern: str) -> typing.Literal[True]:
        if not pattern.startswith("^"):
            raise MissingStartAnchorError(
                f"patterns must have a start anchor (`^`): got `{pattern}`"
            )

        return True

    @staticmethod
    def _has_end_anchor(pattern: str) -> typing.Literal[True]:
        if not pattern.endswith("$"):
            raise MissingEndAnchorError(
                f"patterns must have an end anchor (`$`): got `{pattern}`"
            )

        return True

    @classmethod
    def _validate_patterns(
        cls,
        patterns: typing.Sequence[str] | None,
        checks: typing.Sequence[__PATTERN_VALIDATION_METHODS__] = ("_compiles",),
        allow_none: bool = True,
    ) -> typing.Sequence[str] | None:

        # Return None when allowed if None
        if patterns is None:
            if allow_none:
                return None
            raise ValueError(
                "_validate_patterns called with patterns == `None` when not allowed!"
            )

        # Validate patterns against checks
        for pattern in patterns:
            # Skip patterns `TODO`
            if pattern == "TODO":
                continue

            for check in checks:
                getattr(cls, check)(pattern)

        return patterns

    @pydantic.field_validator("patterns")
    @classmethod
    def validate_patterns(cls, patterns: typing.Sequence[str]) -> typing.Sequence[str]:
        return cls._validate_patterns(
            patterns,
            checks=("_compiles", "_has_start_anchor", "_has_end_anchor"),
            allow_none=False,
        )

    @pydantic.field_validator("start_date_patterns")
    @classmethod
    def validate_start_date_patterns(
        cls, patterns: typing.Sequence[str] | None
    ) -> typing.Sequence[str] | None:
        return cls._validate_patterns(patterns)

    @pydantic.field_validator("end_date_patterns")
    @classmethod
    def validate_end_date_patterns(
        cls, patterns: typing.Sequence[str] | None
    ) -> typing.Sequence[str]:
        return cls._validate_patterns(patterns)
