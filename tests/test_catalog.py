from pathlib import Path

import pytest
from pydantic import ValidationError

from archgen.domain.catalog import NFRCatalog, load_catalog
from archgen.paths import CATALOG_DIR

CORE_KINDS = {
    "latency",
    "throughput",
    "scalability",
    "availability",
    "fault_tolerance",
    "consistency",
}


def catalog() -> NFRCatalog:
    return load_catalog(CATALOG_DIR)


def test_catalog_loads_the_six_core_entries() -> None:
    assert {entry.name for entry in catalog().entries} == CORE_KINDS


def test_catalog_entry_keeps_every_field_from_the_yaml() -> None:
    """내용이 바뀌어도, 스키마가 필드를 흘리지 않는 한 통과한다."""
    for entry in catalog().entries:
        assert entry.meaning
        assert entry.important_when
        assert entry.examples
        assert entry.common_tradeoffs
        for tradeoff in entry.common_tradeoffs:
            assert tradeoff.against
            assert tradeoff.reason


def test_catalog_categories_are_written_in_upper_case() -> None:
    for entry in catalog().entries:
        assert entry.category.isupper()


def one_line(text: str) -> str:
    """직렬화가 한 필드를 한 줄로 펴므로, 비교 전에 같은 모양으로 맞춘다."""
    return " ".join(text.split())


def test_prompt_block_groups_every_entry_under_its_category() -> None:
    block = catalog().to_prompt_block()

    section = ""
    placed: dict[str, str] = {}
    for line in block.splitlines():
        if line.startswith("["):
            section = line.strip("[]")
        elif line.startswith("- "):
            placed[line[2:].split(":")[0]] = section

    assert placed == {entry.name: entry.category for entry in catalog().entries}


def test_prompt_block_carries_every_field_of_each_entry() -> None:
    block = catalog().to_prompt_block()

    for entry in catalog().entries:
        assert one_line(entry.meaning) in block
        for condition in entry.important_when:
            assert one_line(condition) in block
        for example in entry.examples:
            assert one_line(example) in block
        for tradeoff in entry.common_tradeoffs:
            assert tradeoff.against in block
            assert one_line(tradeoff.reason) in block


def test_prompt_block_lists_categories_in_a_fixed_order() -> None:
    """파일 읽는 순서가 달라져도 프롬프트 문자열은 같아야 한다."""
    block = catalog().to_prompt_block()

    headers = [line for line in block.splitlines() if line.startswith("[")]
    assert headers == sorted(headers)
    assert len(headers) == len(set(headers)), "같은 카테고리가 흩어져 두 번 나왔다"


MULTILINE_ENTRY = """
name: latency
category: PERFORMANCE
meaning: |-
  여러 줄로 쓴
  뜻 설명
important_when:
  - |-
    여러 줄로 쓴
    중요한 경우
examples:
  - |-
    여러 줄로 쓴
    예시
common_tradeoffs:
  - against: cost
    reason: |-
      여러 줄로 쓴
      이유
""".strip()


def test_prompt_block_keeps_one_line_per_field(tmp_path: Path) -> None:
    """yaml에 줄바꿈이 남아 있어도 블록은 한 필드당 한 줄을 지킨다."""
    (tmp_path / "multiline.yaml").write_text(MULTILINE_ENTRY, encoding="utf-8")

    block = load_catalog(tmp_path).to_prompt_block()

    assert len(block.splitlines()) == 5, "헤더 1줄 + 필드 4줄이어야 한다"
    assert "여러 줄로 쓴 뜻 설명" in block


def test_load_catalog_rejects_an_empty_directory(tmp_path: Path) -> None:
    """카탈로그가 비면 프롬프트가 조용히 비므로, 로드 시점에 막는다."""
    with pytest.raises(ValueError, match="비어"):
        load_catalog(tmp_path)


def test_load_catalog_rejects_duplicate_names(tmp_path: Path) -> None:
    """kind는 어휘의 기준이라 같은 이름이 두 번 나오면 안 된다."""
    for filename in ("a.yaml", "b.yaml"):
        (tmp_path / filename).write_text(MULTILINE_ENTRY, encoding="utf-8")

    with pytest.raises(ValueError, match="latency"):
        load_catalog(tmp_path)


ENTRY = """name: latency
category: PERFORMANCE
meaning: 뜻
important_when: [조건]
examples: [예]
common_tradeoffs: [{against: cost, reason: 이유}]
"""


@pytest.mark.parametrize(
    ("original", "emptied"),
    [
        ("name: latency", 'name: ""'),
        ("category: PERFORMANCE", 'category: ""'),
        ("meaning: 뜻", 'meaning: ""'),
        ("important_when: [조건]", "important_when: []"),
        ("examples: [예]", "examples: []"),
        ("common_tradeoffs: [{against: cost, reason: 이유}]", "common_tradeoffs: []"),
        ("{against: cost, reason: 이유}", '{against: "", reason: 이유}'),
        ("{against: cost, reason: 이유}", '{against: cost, reason: ""}'),
        ("name: latency", 'name: "   "'),
        ("meaning: 뜻", 'meaning: "   "'),
    ],
)
def test_load_catalog_rejects_an_empty_field(
    tmp_path: Path, original: str, emptied: str
) -> None:
    """빈 값은 프롬프트에 빈 줄로 나가 조용히 품질만 떨어뜨린다."""
    (tmp_path / "a.yaml").write_text(ENTRY.replace(original, emptied), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_catalog(tmp_path)


def test_load_catalog_rejects_an_unknown_field(tmp_path: Path) -> None:
    """yaml 키 오타는 해당 필드를 조용히 비게 만든다."""
    (tmp_path / "a.yaml").write_text(ENTRY + "exmaples: [오타]\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        load_catalog(tmp_path)


def test_load_catalog_rejects_a_missing_directory(tmp_path: Path) -> None:
    """경로를 잘못 넘긴 것과 내용이 빈 것은 고쳐야 할 곳이 다르다."""
    with pytest.raises(ValueError, match="디렉터리가 없다"):
        load_catalog(tmp_path / "missing")


def test_load_catalog_reads_yml_files_too(tmp_path: Path) -> None:
    """확장자 하나 때문에 항목이 통째로 빠지면 아무도 알아채지 못한다."""
    (tmp_path / "a.yaml").write_text(ENTRY, encoding="utf-8")
    (tmp_path / "b.yml").write_text(ENTRY.replace("latency", "throughput"), encoding="utf-8")

    catalog = load_catalog(tmp_path)

    assert {entry.name for entry in catalog.entries} == {"latency", "throughput"}


def test_nfr_catalog_rejects_having_no_entries() -> None:
    """로더를 거치지 않고 만들어도 빈 카탈로그는 프롬프트를 조용히 비운다."""
    with pytest.raises(ValidationError):
        NFRCatalog(entries=[])
