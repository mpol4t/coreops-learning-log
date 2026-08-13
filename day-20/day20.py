import json
import csv
import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

def parse_json(dosyaj):
# JSON dosyamızın parse fonksiyonu!
    with open(dosyaj, encoding="utf-8") as file:
        loaded = json.load(file)
        return loaded

def parse_csv(dosyac):
# CSV dosyamızın parse fonksiyonu!
    with open(dosyac, encoding="utf-8",newline="") as file:
        reader = csv.DictReader(file)
        içerik = []
        for record in reader:
            içerik.append(record)
        return içerik
    
def jnormalization(dosyaj):
# JSON dosyamızın normalization fonksiyonu!
    temiz_dict = {}
    if "asset_id" in dosyaj:
        if isinstance(dosyaj["asset_id"], str):
            temiz_dict["asset_id"] = dosyaj["asset_id"].strip()
            
        else:
            temiz_dict["asset_id"] = dosyaj["asset_id"]
     
    if "hostname" in dosyaj:    
        if isinstance(dosyaj["hostname"], str):
            temiz_dict["hostname"] = dosyaj["hostname"].strip()
        else:
            temiz_dict["hostname"] = dosyaj["hostname"]
            
    temiz_dict["source"] = "json"
    
    if "port" in dosyaj:
        temiz_dict["port"] = dosyaj["port"]
        
    if "active" in dosyaj:
        temiz_dict["active"] = dosyaj["active"]
    
    return temiz_dict

def cnormalization(dosyac):
# CSV dosyamızın normalizasyon fonksiyonu!
    temiz_dict = {}
    if "asset_id" in dosyac:
        temiz_dict["asset_id"] = dosyac["asset_id"].strip()
        
    if "hostname" in dosyac:    
        temiz_dict["hostname"] = dosyac["hostname"].strip()
    
    if "port" in dosyac:    
        temiz_dict["port"] = int(dosyac["port"].strip())
    
    if "active" in dosyac:
        temiz_dict["active"] = dosyac["active"].strip().lower()
        
        if temiz_dict["active"] == "true":
            temiz_dict["active"] = True
            
        elif temiz_dict["active"] == "false":
            temiz_dict["active"] = False
            
        else:
            raise ValueError("Girilen veri değeri boolean değil!")
        
    temiz_dict["source"] = "csv"

    return temiz_dict

def validation(dosya):
# Normalize edilen dosyalarımızın valid olup olmadığının kontrolünü yapan fonksiyon!
    required = ["asset_id", "hostname", "port", "active", "source"]
    for x in required:
        if not x in dosya:
            raise ValueError(f"Gereken {x} parametresi bulunamadı.")
    
    if not isinstance(dosya["asset_id"], str):
        raise ValueError("Asset_id'nin tipi string değil!")
    if not dosya["asset_id"]:
        raise ValueError("Asset_id boş olamaz!")

    if not isinstance(dosya["hostname"], str):
        raise ValueError("Hostname'in tipi string değil!")
    if not dosya["hostname"]:
        raise ValueError("Hostname değeri boş string olamaz!")
    
    if type(dosya["port"]) is not int:
        raise ValueError("Port değerinin tipi integer değil!")
    elif not 1<= dosya["port"] <= 65535:
        raise ValueError("Port belirtilen aralıklarda değil!")
    
    if type(dosya["active"]) is not bool:
        raise ValueError("Active değerinin tipi boolean değil!")
    
    if not isinstance(dosya["source"], str):
        raise ValueError("Source değerinin tipi string değil!")
    if dosya["source"] != "csv" and dosya["source"] != "json":
        raise ValueError("Source beklenenden farklı bir değer!")

    
def main():
# Orkestra şefimiz!
    j_accepted = 0
    j_rejected = 0
    c_accepted = 0
    c_rejected = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("JSON_FILE")
    parser.add_argument("CSV_FILE")
    args = parser.parse_args()
    j_dosyası = []
    c_dosyası = []
    
    try:
        j_dosyası = parse_json(args.JSON_FILE) 
    except json.JSONDecodeError as hata:
        logging.warning(
            "event=file_parse_failed, source=json, hata=%s",
            hata
        )
        
    try:   
        c_dosyası = parse_csv(args.CSV_FILE)
    except UnicodeDecodeError as hata:
        logging.warning(
            "event=file_parse_failed, source=csv, hata=%s",
            hata 
        )
    
    with open("normalized.jsonl", "w", encoding="utf-8") as output:
        
        for record in j_dosyası:
            try:
                j_normal = jnormalization(record)
                validation(j_normal)
                output.write(json.dumps(j_normal) + "\n")
                j_accepted +=1
                
            except ValueError as hata:
                j_rejected += 1
                logging.warning(
                    "event=record_rejected, source=json, error=%s",
                    hata
                )
            
        for record in c_dosyası:
            try:
                c_normal = cnormalization(record)
                validation(c_normal)
                output.write(json.dumps(c_normal) + "\n")
                c_accepted += 1
                
            except ValueError as hata:
                c_rejected += 1
                logging.warning(
                    "event=record_rejected, source=csv, error=%s",
                    hata
                )
        
        
    logging.info(
        "event=processing_complete, JSON_accepted=%s, JSON_rejected=%s, CSV_accepted=%s, CSV_rejected=%s, TOTAL_accepted=%s, TOTAL_rejected=%s",
        j_accepted, j_rejected, c_accepted, c_rejected,
        j_accepted + c_accepted, j_rejected + c_rejected 
    )
        

if __name__ == "__main__":
    sys.exit(main())