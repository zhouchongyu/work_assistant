from __future__ import annotations

import re
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict


_first_cap_re = re.compile("(.)([A-Z][a-z]+)")
_all_cap_re = re.compile("([a-z0-9])([A-Z])")


def to_camel(string: str) -> str:
    # snake_case -> camelCase
    parts = string.split("_")
    if not parts:
        return string
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class Schema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )

