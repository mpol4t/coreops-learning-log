import argparse
import json
import logging
import sys

from asset_model.models import Asset

logging.basicConfig(level=logging.INFO, format="%(levelname)s, %(message)s")
logger = logging.getLogger(__name__)


def parser_file(dosya):
    with open(dosya, encoding="utf-8") as file:
        loaded = json.load(file)

        if not isinstance(loaded, list):
            raise TypeError("Top-Level JSON bir liste olmalı!")

        return loaded


def normalization(loaded):
    temiz_dict = {}
    temiz_tags = []
    if "asset_id" in loaded:
        if isinstance(loaded["asset_id"], str):
            temiz_dict["asset_id"] = loaded["asset_id"].strip()
        else:
            temiz_dict["asset_id"] = loaded["asset_id"]

    if "hostname" in loaded:
        if isinstance(loaded["hostname"], str):
            temiz_dict["hostname"] = loaded["hostname"].strip()
        else:
            temiz_dict["hostname"] = loaded["hostname"]

    if "port" in loaded:
        temiz_dict["port"] = loaded["port"]

    if "active" in loaded:
        temiz_dict["active"] = loaded["active"]

    if "tags" in loaded:
        if isinstance(loaded["tags"], list):
            for x in loaded["tags"]:
                if isinstance(x, str):
                    x = x.strip()
                temiz_tags.append(x)

            temiz_dict["tags"] = temiz_tags

        else:
            temiz_dict["tags"] = loaded["tags"]

    return temiz_dict


def validation(temiz_dict):
    required = ["asset_id", "hostname", "port", "active", "tags"]

    if not isinstance(temiz_dict, dict):
        raise TypeError("Girilen veri istenen veri tipi ile uyuşmadı!")

    for x in required:
        if x not in temiz_dict:
            raise TypeError(f"Gerekli field bulunamadı: {x}")

    if not isinstance(temiz_dict["asset_id"], str):
        raise TypeError("Asset_id filed'Inın tipi str olması gerekiyordu!")
    elif not temiz_dict["asset_id"]:
        raise TypeError("Asset_id boş olmamalı!")

    if not isinstance(temiz_dict["hostname"], str):
        raise TypeError("Hostname field'ının tipi str olması gerekiyordu!")
    elif not temiz_dict["hostname"]:
        raise TypeError("Hostname boş olmamalı!")

    if not type(temiz_dict["port"]) is int:
        raise TypeError("Port field'ının integer olması gerekiyor!")
    else:
        if not 0 < temiz_dict["port"] < 65536:
            raise TypeError(
                "Port değeri beklenen aralıkta değil! (Beklenen aralık: 1-65535)"
            )

    if not type(temiz_dict["active"]) is bool:
        raise TypeError("Active değerinin tipi bool olması gerekiyordu!")

    if not isinstance(temiz_dict["tags"], list):
        raise TypeError("Tags field'ının değeri list olması gerekiyordu!")
    else:
        for x in temiz_dict["tags"]:
            if not isinstance(x, str):
                raise TypeError(
                    "Tags listesi içindeki değerlerin string olması gerekiyor!"
                )
            elif not x:
                raise TypeError("Tags liste içindeki değerler boş olmamalı!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    accepted = 0
    rejected = 0
    try:
        loaded = parser_file(args.file)
    except json.JSONDecodeError as hata:
        logger.warning("event=file_parse_failed, hata=%s", hata)
        return 47

    with open("output.jsonl", "w", encoding="utf-8") as file:
        for record in loaded:
            try:
                normalized = normalization(record)
                validation(normalized)
                asset = Asset(
                    asset_id=normalized["asset_id"],
                    hostname=normalized["hostname"],
                    port=normalized["port"],
                    active=normalized["active"],
                    tags=normalized["tags"],
                )
                yazılacak = {}
                yazılacak["asset_id"] = asset.asset_id
                yazılacak["hostname"] = asset.hostname
                yazılacak["port"] = asset.port
                yazılacak["active"] = asset.active
                yazılacak["tags"] = asset.tags

                file.write(json.dumps(yazılacak) + "\n")
                accepted += 1

            except (TypeError, ValueError) as hata:
                rejected += 1
                logger.warning("event=record_rejected, hata=%s", hata)

    logger.info(
        "event=processing_completed, accepted=%s, rejected=%s", accepted, rejected
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
