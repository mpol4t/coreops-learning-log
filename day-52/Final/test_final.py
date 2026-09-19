import json

from final import ReportConfig, parse_config, run


# =========================================================
# ESKİ DAVRANIŞLAR — REGRESSION TESTLERİ
# =========================================================

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


# =========================================================
# YENİ REQUIREMENT — OPTIONAL --output
# =========================================================

def test_explicit_output_path_is_preserved(tmp_path):
    input_file = tmp_path / "sample.jsonl"
    output_file = tmp_path / "benim-sonucum.json"

    input_file.write_text(
        '{"id": 1, "name": "alpha"}\n',
        encoding="utf-8"
    )

    config = parse_config([
        "--input", str(input_file),
        "--output", str(output_file),
        "--format", "json",
    ])

    assert config.output_path == output_file

    run(config)

    assert output_file.exists()

    parsed = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert parsed == {
        "total_records": 1
    }


def test_implicit_json_output_path(tmp_path):
    input_file = tmp_path / "sample.jsonl"

    input_file.write_text(
        '{"id": 1, "name": "alpha"}\n'
        '{"id": 2, "name": "beta"}\n',
        encoding="utf-8"
    )

    config = parse_config([
        "--input", str(input_file),
        "--format", "json",
    ])

    expected_output = tmp_path / "sample.report.json"

    assert config.output_path == expected_output

    run(config)

    assert expected_output.exists()

    parsed = json.loads(
        expected_output.read_text(encoding="utf-8")
    )

    assert parsed == {
        "total_records": 2
    }


def test_implicit_csv_output_path(tmp_path):
    input_file = tmp_path / "sample.jsonl"

    input_file.write_text(
        '{"id": 1, "name": "alpha"}\n'
        '{"id": 2, "name": "beta"}\n',
        encoding="utf-8"
    )

    config = parse_config([
        "--input", str(input_file),
        "--format", "csv",
    ])

    expected_output = tmp_path / "sample.report.csv"

    assert config.output_path == expected_output

    run(config)

    assert expected_output.exists()

    result = expected_output.read_text(encoding="utf-8")

    assert result.splitlines() == [
        "total_records",
        "2"
    ]