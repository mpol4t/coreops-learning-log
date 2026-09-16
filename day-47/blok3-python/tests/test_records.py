from src.records import iter_records
import pytest
import json

def test_function(tmp_path):
    input_file = tmp_path / "records.jsonl"

    input_file.write_text(
        '{"id": 10, "name": "alpha"}\n{"id":20, "name": "beta"}',
        encoding="utf-8"
    )

    records = list(iter_records(input_file))

    assert len(records) == 2
    assert records[1]["name"] == "beta"

def test_malformed(tmp_path):
    input_file = tmp_path / "malformed.jsonl"

    input_file.write_text(
        '{"id": 10, "name": "alpha"'
    )

    with pytest.raises(json.JSONDecodeError):
        records = list(iter_records(input_file))
