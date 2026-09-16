import json

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
