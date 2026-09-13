import json
import sys

def iter_records(path):
    try:
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
            

    except json.JSONDecodeError:
        print("JSON dosyasının formatında bir hata meydana geldi!", file=sys.stderr)
        sys.exit(1)
        
        
        
def iter_high_risk(records, minimum):
    for record in records:
        if record["risk"] >= minimum:
            yield record

def main():
    records = iter_records("assets.jsonl")
    for record in iter_high_risk(records, 70):
        print(record["hostname"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
