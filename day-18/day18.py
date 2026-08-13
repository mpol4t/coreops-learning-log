import json
import argparse
import sys

def parse_json(dosya):
    with open(dosya, encoding="utf-8") as dosya:
            loaded = json.load(dosya)
            return loaded

def validation(loaded):
    required = ["asset_id", "hostname", "port", "active", "tags"]
    same_str_rule = ["asset_id", "hostname"]
    
    if not isinstance(loaded, dict):
        raise ValueError
    
    for x in required:
        if x not in loaded:
            raise ValueError(f"{x} eksik!")
        
    for x in same_str_rule:
        if not isinstance(loaded[x], str):
            raise ValueError(f"{x}'in değeri yanlış!")
        if not loaded[x].strip():
            raise ValueError

    if type(loaded["port"]) is not int:
        raise ValueError("Port için value değeri hatalı!")
    elif not 1 <= loaded["port"] <= 65535:
        raise ValueError("Port değeri geçerli aralıkta değil!")
    
    if type(loaded["active"]) is not bool:
        raise ValueError("Active değeri boolean değil!")
    
    if type(loaded["tags"]) is not list:
        raise ValueError("Tags liste değil!")

    for x in loaded["tags"]:
        if type(x) is not str:
            raise ValueError("Tags değerlerinin tipi string değil!")
    

def normalization(veri):
    strip_required = ["asset_id", "hostname"]
    temiz_tagler = []
    temiz_dict = {}
    
    for x in strip_required:
        temiz = veri[x].strip()
        temiz_dict[x] = temiz
    
    for x in veri["tags"]:
        temiz = x.strip()
        temiz_tagler.append(temiz)

    temiz_dict["port"] = veri["port"]
    temiz_dict["active"] = veri["active"]
    temiz_dict["tags"] = temiz_tagler
    
    return temiz_dict

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("file")
        args = parser.parse_args()
        json_verisi = parse_json(args.file)
        validation(json_verisi)
        normalize = normalization(json_verisi)
        print(normalize)
        return 0
    
    except json.JSONDecodeError:
        print("JSON Decode edilirken hata meydana geldi!", file=sys.stderr)
        return 22
    
    except ValueError as hata:
        print(f"Hata meydana geldi: {hata}", file=sys.stderr)
        return 11


if __name__ == "__main__":
    sys.exit(main())