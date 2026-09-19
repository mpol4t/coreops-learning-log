import json

from day52 import ReportConfig, run


def test_csv_report_without_max_records(tmp_path):
    input_file = tmp_path / "sample.jsonl"
    output_file = tmp_path / "report.csv"

    input_file.write_text(
        '{"id": 1, "name": "alpha"}\n'
        '{"id": 2, "name": "beta"}\n'
        '{"id": 3, "name": "gamma"}\n',
        encoding="utf-8"
    )

    config = ReportConfig(
        input_path=input_file,
        output_path=output_file,
        output_format="csv",
        max_records=None
    )

    run(config)

    result = output_file.read_text(encoding="utf-8")

    assert result.splitlines() == [
        "total_records",
        "3"
    ]


def test_json_report_without_max_records(tmp_path):
    input_file = tmp_path / "sample.jsonl"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        '{"id": 1, "name": "alpha"}\n'
        '{"id": 2, "name": "beta"}\n'
        '{"id": 3, "name": "gamma"}\n',
        encoding="utf-8"
    )

    config = ReportConfig(
        input_path=input_file,
        output_path=output_file,
        output_format="json",
        max_records=None
    )

    run(config)

    result = output_file.read_text(encoding="utf-8")
    parsed = json.loads(result)

    assert parsed == {
        "total_records": 3
    }


def test_json_report_with_max_records_2(tmp_path):
    input_file = tmp_path / "sample.jsonl"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        '{"id": 1, "name": "alpha"}\n'
        '{"id": 2, "name": "beta"}\n'
        '{"id": 3, "name": "gamma"}\n',
        encoding="utf-8"
    )

    config = ReportConfig(
        input_path=input_file,
        output_path=output_file,
        output_format="json",
        max_records=2
    )

    run(config)

    result = output_file.read_text(encoding="utf-8")
    parsed = json.loads(result)

    assert parsed == {
        "total_records": 2
    }