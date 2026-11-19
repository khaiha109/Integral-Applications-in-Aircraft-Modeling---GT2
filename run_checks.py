"""Chạy các kiểm thử có nội dung và ghi trạng thái cho dashboard.

Hai test của phần Khải trong test_basic.py đã được Khải hoàn thiện (19/11/2026),
nên không còn test khung nào bị loại khỏi thống kê.
# AI-assisted: xem AI_DECLARATION.md
"""

from __future__ import annotations

import io
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
PLACEHOLDERS: set[str] = set()   # không còn test khung `pass`


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main() -> int:
    loader = unittest.TestLoader()
    discovered = loader.discover(str(ROOT / "tests"), pattern="test_*.py")
    tests = list(flatten(discovered))
    excluded = [test for test in tests if test._testMethodName in PLACEHOLDERS]
    selected = [test for test in tests if test._testMethodName not in PLACEHOLDERS]
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.TestSuite(selected))
    output = stream.getvalue()
    data = {
        "time": datetime.now(ZoneInfo("Asia/Bangkok")).isoformat(timespec="seconds"),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "excluded_placeholders": len(excluded),
        "success": result.wasSuccessful(),
        "output": output,
    }
    ROOT.joinpath("results").mkdir(exist_ok=True)
    (ROOT / "results" / "test_results.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(output)
    if excluded:
        print(f"Đã bỏ qua {len(excluded)} test khung 'pass' vì chưa có nội dung kiểm tra.")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
