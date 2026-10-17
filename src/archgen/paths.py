"""저장소 안의 자원 경로를 한 곳에서 정한다."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCES = PROJECT_ROOT / "resources"

CATALOG_DIR = RESOURCES / "catalog"
GOLDEN_DIR = RESOURCES / "golden"
