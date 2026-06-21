from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from taobao_analysis.pipeline import run_pipeline


def main() -> None:
    artifacts = run_pipeline()
    print("Analysis complete.")
    print(json.dumps({"overview": artifacts.overview, "funnel": artifacts.funnel}, ensure_ascii=False, indent=2))
    print(f"Report written to: {artifacts.report_path}")


if __name__ == "__main__":
    main()
