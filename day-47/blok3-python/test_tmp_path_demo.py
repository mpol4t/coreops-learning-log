import json


def test_one_jsonl_record(tmp_path):
    input_file = tmp_path / "records.jsonl"

    input_file.write_text(
        '{"name":"alpha","count":3}\n{"name":"beta","count":7}\n',
        encoding="utf-8"
    )

    lines = input_file.read_text(encoding="utf-8").splitlines()
    records = json.loads(lines[1])
    assert records["name"] == "beta"
