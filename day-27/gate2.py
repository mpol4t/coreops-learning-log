import json
import sys
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

def json_parser(dosya):
    with open(dosya, encoding="utf-8") as file:
        loaded = json.load(file)

        if not isinstance(loaded, list):
            raise ValueError("Top-level JSON bir liste olmalı!")

        return loaded
    
def normalization(loaded):
    temiz_dosya = {}
    temiz_tagler = []
    
    if "asset_id" in loaded:
        if isinstance(loaded["asset_id"], str):
            temiz_dosya["asset_id"] = loaded["asset_id"].strip()
        else:
            temiz_dosya["asset_id"] = loaded["asset_id"]
    
    if "hostname" in loaded:
        if isinstance(loaded["hostname"], str):
            temiz_dosya["hostname"] = loaded["hostname"].strip()
        else:
            temiz_dosya["hostname"] = loaded["hostname"]
            
    if "port" in loaded:
        temiz_dosya["port"] = loaded["port"]
            
    if "active" in loaded:
        temiz_dosya["active"] = loaded["active"]
        
    if "tags" in loaded:
        if isinstance(loaded["tags"], list):
            for x in loaded["tags"]:
                if isinstance(x, str):
                    x = x.strip()
                temiz_tagler.append(x)
        
            temiz_dosya["tags"] = temiz_tagler
            
        else:
            temiz_dosya["tags"] = loaded["tags"]
            
    return temiz_dosya
    
def validation(temiz_dosya):
    required = ["asset_id", "hostname", "port", "active", "tags"]
    
    if not isinstance(temiz_dosya, dict):
        raise ValueError("Validation'a gelen veriler dict değil!")
    
    for x in required:
        if not x in temiz_dosya:
            raise ValueError(f"Dictionary içinde {x} bulunamadı!")
        
    if not isinstance(temiz_dosya["asset_id"], str):
        raise ValueError("asset_id string olması gerekiyor!")
    
    if not isinstance(temiz_dosya["hostname"], str):
        raise ValueError("hostname string olması gerekiyor!")
    
    if type(temiz_dosya["port"]) is not int:
        raise ValueError("port integer olması gerekiyor!")
    
    elif not 1 <= temiz_dosya["port"] <= 65535:
        raise ValueError("port istenen değer aralığında değil!")
    
    if type(temiz_dosya["active"]) is not bool:
        raise ValueError("active değeri boolean olması gerekiyor!")
    
    if not isinstance(temiz_dosya["tags"], list):
        raise ValueError("tags değeri liste olması gerekiyor!")
    else:
        for x in temiz_dosya["tags"]:
            if not isinstance(x, str):
                raise ValueError("Liste içindeki değerlerin string olması gerekiyor!")
            

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dosya")
    args = parser.parse_args()
    accepted = 0
    rejected = 0
    parsered = []
    try:
        parsered = json_parser(args.dosya)
    except json.JSONDecodeError as hata:
        logging.warning(
            "event=file_parse_failed, hata=%s",
            hata
        )
        return 47
    except ValueError as hata:
        logging.warning(
            "event=input_contract_failed, hata=%s",
            hata
        )
        return 48
    
    with open("output.jsonl", "w", encoding="utf-8") as file:
        for record in parsered:
            try:
                normalizaed = normalization(record)
                validation(normalizaed)
                file.write(json.dumps(normalizaed) + "\n")
                accepted += 1
        
            except ValueError as hata:
                rejected += 1
                logging.warning(
                    "event=record_rejected, hata=%s",
                    hata
                )
                
    logging.info(
        "event=processing_complete, accepted=%s, rejected=%s",
        accepted,
        rejected
    )
    
    return 0
    

if __name__ == "__main__":
    sys.exit(main())