"""실행: uv run python try_generation.py '실시간 채팅 서비스'.

Research → NFR 선정 → 루브릭 → 하네스 → 렌더 검증을 실행한다.
Judge는 실제 오탐 검증 전까지 기본 비활성화한다.
로그·중간 결과·최종 결과는 .archgen/generation/<실행>/에 저장한다.
"""

import argparse
import logging
import sys

from archgen.core.service import run_generation
from archgen.domain.brief import InterviewBrief, Seniority


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic", nargs="?", default="실시간 채팅 서비스")
    parser.add_argument("--seniority", choices=list(Seniority), default=Seniority.MIDDLE)
    # parser.add_argument("--notes")
    args = parser.parse_args(argv)
    logger = logging.getLogger("archgen")
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    try:
        brief = InterviewBrief(Seniority(args.seniority), args.topic)
        result = run_generation(brief)
        print(f"결과: {result['status']}\n저장 위치: {result['output_dir']}")
        return 0 if result["status"] == "complete" else 1
    except Exception as error:  # noqa: BLE001 — CLI 경계에서 실패를 표시하고 종료 코드를 반환한다.
        print(f"생성 실패: {error}", file=sys.stderr)
        return 1
    finally:
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    raise SystemExit(main())
