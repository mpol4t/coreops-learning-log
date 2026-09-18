import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReportConfig:
    input_path: Path
    output_path: Path


def parse_config(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args(argv)

    return ReportConfig(
        input_path=Path(args.input),
        output_path=Path(args.output),
    )


def build_report(text: str) -> dict:
    lines = [line for line in text.splitlines() if line.strip()]

    return {
        "line_count": len(lines),
    }


def run(config: ReportConfig) -> None:
    text = config.input_path.read_text(encoding="utf-8")

    report = build_report(text)

    config.output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )


def main(argv=None) -> int:
    config = parse_config(argv)
    run(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())