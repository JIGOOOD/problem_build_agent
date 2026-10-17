"""NFR Agent가 작성한 본문에 허용하지 않은 언어가 섞였는지 검사한다."""

import re
import unicodedata

_LETTERS = re.compile(
    r"[A-Za-z\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\uac00-\ud7a3\ud7b0-\ud7ff]"
)
_WORD = r"[A-Za-z]+(?:[-'][A-Za-z]+)*"
# shortcut: 연속 단어 수로 긴 영어를 판정한다. 용어 오탐이 누적되면 기준을 재검토한다.
_LONG_ENGLISH = re.compile(rf"\b{_WORD}(?:\s+{_WORD}){{4,}}\b")


def check_language(value, path="") -> list[str]:
    """식별자와 참조를 제외한 생성 본문의 위반 위치를 반환한다."""
    if isinstance(value, dict):
        return [
            error
            for key, item in value.items()
            if key not in {"id", "related_nfr_ids", "evidence_refs"}
            for error in check_language(item, f"{path}.{key}" if path else key)
        ]
    if isinstance(value, list):
        return [
            error
            for index, item in enumerate(value)
            for error in check_language(item, f"{path}[{index}]")
        ]
    if isinstance(value, str):
        for char in value:
            if unicodedata.category(char)[0] in {"L", "M"} and not _LETTERS.fullmatch(
                char
            ):
                return [
                    f"{path}: 허용하지 않은 언어 문자 {char!r}. 설명은 한국어로 작성하세요."
                ]
        match = _LONG_ENGLISH.search(value)
        if match:
            return [
                (
                    f"{path}: 연속 영문 5단어 이상 {match.group()!r}. "
                    "영어는 짧은 기술 용어에만 사용하고 설명은 한국어로 작성하세요."
                )
            ]
    return []
