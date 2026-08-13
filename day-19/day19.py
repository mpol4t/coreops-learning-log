import json, csv, argparse, sys, logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

def basic_normalize(satır):
    normalized = {}
    normalized["asset_id"] = satır["asset_id"].strip()
    normalized["hostname"] = satır["hostname"].strip()
    normalized["port"] = int(satır["port"].strip())
    normalized["active"] = satır["active"].strip().lower()
    if normalized["active"] == "true":
        normalized["active"] = True
    elif normalized["active"] == "false":
        normalized["active"] = False
    else:
        raise ValueError("Boolean tipi yanlış!")
    return normalized

def validate(satır):
    if not satır["asset_id"]:
        raise ValueError("asset_id boş olamaz!")
    
    if not satır["hostname"]:
        raise ValueError("hostname boş olamaz!")
    
    if not 1 <= satır["port"] <= 65535:
        raise ValueError("Port değeri geçerli aralıkta değil!")

def main():
    accepted = 0
    rejected = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("dosya")
    args = parser.parse_args()
    with open(args.dosya, encoding="utf-8") as dosya:
        içerik = csv.DictReader(dosya)
        for satır in içerik:
            try:
                normalized = basic_normalize(satır)
                validate(normalized)
                print(json.dumps(normalized))
                accepted += 1
                logging.info("event=record_accepted, asset_id=%s", normalized["asset_id"])
    
            except ValueError as hata:
                rejected += 1 
                logging.warning(
                    "event=%s, asset_id=%s, reason=%s",
                    "record_rejected", 
                    satır.get("asset_id"),
                    hata
                )
        logging.info("event=processing_complete, accepted=%s, rejected=%s", 
                     accepted, 
                     rejected)
        return 0
                
if __name__ == "__main__":
    sys.exit(main())
