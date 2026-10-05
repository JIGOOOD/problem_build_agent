"""검사가 남기는 지적 하나. 하네스와 Judge가 같은 형식을 쓴다."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, StringConstraints

# 공백만 있는 값도 비어 있는 것으로 본다.
NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Severity(StrEnum):
    """ERROR는 repair 대상, WARN은 기록만 한다."""

    ERROR = "ERROR"
    WARN = "WARN"


class Finding(BaseModel):
    """어느 위치(path)에서 어떤 규칙(code)이 깨졌는지."""

    code: NonBlank
    severity: Severity
    path: NonBlank
    message: NonBlank
