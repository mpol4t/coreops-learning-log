import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True)
class ReportConfig:
    input_path: Path
    output_path: Path


def parse_config() -> ReportConfig:

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    return ReportConfig(
        input_path=Path(args.input),
        output_path=Path(args.output),
    )

def iter_records(path):
    with open(path , encoding="utf-8") as dosya:
        for x in dosya:
            cleaned = x.strip()
            if cleaned:
                json_params = json.loads(cleaned)
                if isinstance(json_params, dict):
                    yield json_params
                else:
                    raise ValueError("Değerlerimiz dict olmalı!")

            else:
                raise ValueError("Gelen veri boş olmamalı!")


def build_report(records):
    record_list = list(records)

    return {
        "total_records": len(record_list),
    }


def run(config: ReportConfig) -> None:
    records = iter_records(config.input_path)

    report = build_report(records)

    config.output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

def main() -> int:
    config = parse_config()
    run(config)
    return 0

if __name__ == "__main__":
    sys.exit(main())