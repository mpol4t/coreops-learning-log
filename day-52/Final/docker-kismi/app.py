import json
from pathlib import Path

OUTPUT = Path("/lab/runtime/report.json")

print(f"output_path={OUTPUT}", flush=True)

report = {
    "status": "ok",
    "total_records": 3
}

OUTPUT.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

print("report_written=true", flush=True)
