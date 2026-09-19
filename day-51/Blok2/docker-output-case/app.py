from pathlib import Path
import json

output_path = Path("/lab/runtime/report.json")

output_path.parent.mkdir(parents=True, exist_ok=True)

report = {
    "status": "ok",
    "source": "docker-output-case",
}

output_path.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print("report written")
