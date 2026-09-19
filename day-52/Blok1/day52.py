import argparse
import sys
import json
import csv
from dataclasses import dataclass
from pathlib import Path
from itertools import islice

@dataclass(frozen=True)
class ReportConfig:
    input_path: Path
    output_path: Path
    output_format: str
    max_records: int | None = None
    
def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--max-records", type=int, default=None)
    
    args = parser.parse_args()
    
    if args.max_records is not None and args.max_records <= 0:
        raise parser.error("Max_records değeri sıfır veya daha küçük olamaz!!")
    
    return ReportConfig(
        input_path=Path(args.input),
        output_path=Path(args.output),
        output_format=args.format,
        max_records=args.max_records    
    )
    
def iter_records(path):
    with open(path, encoding="utf-8") as dosya:
        for satır in dosya:
            cleaned = satır.strip()
            if cleaned:
                json_params = json.loads(cleaned)
                if isinstance(json_params, dict):
                    yield json_params
                    
                else:
                    raise ValueError("Değerler dict olmalı!")
            
            else:
                raise ValueError("Gelen veri boş olmamalı!")
            

def build_report(records):
    record_list = list(records)
    
    return {
        "total_records": len(record_list)
    }
    
def write_json_report(report, output_path):
    text = json.dumps(report, indent=2)
    output_path.write_text(text, encoding="utf-8")
    
def write_csv_report(report, output_path):
    with open(output_path, "w", encoding="utf-8", newline="") as dosya:
        writer = csv.DictWriter(
            dosya,
            fieldnames=report.keys()
        )

        writer.writeheader()
        writer.writerow(report)
        
def run(config):
    records = iter_records(config.input_path)
    
    if config.max_records is not None:
        records = islice(records, config.max_records)
    
    report = build_report(records)
    
    if config.output_format == "json":
        write_json_report(report, config.output_path)
    
    elif config.output_format == "csv":
        write_csv_report(report, config.output_path)
        
def main():
    config = parse_config()
    run(config)
    return 0

if __name__ == "__main__":
    sys.exit(main())