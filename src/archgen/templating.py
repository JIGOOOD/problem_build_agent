"""Jinja2 템플릿 환경. md 렌더와 LLM 프롬프트가 같은 규칙으로 글을 만든다."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def template_env(templates_dir: Path) -> Environment:
    """제어문이 빈 줄·공백을 남기지 않고, 변수 이름을 틀리면 조용히 넘어가지 않는 환경."""
    return Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        # 변수 이름을 틀리면 빈 문자열로 조용히 넘어가지 않고 실패한다.
        undefined=StrictUndefined,
    )
