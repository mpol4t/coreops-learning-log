import logging
import sys
import uuid

from repository import get_connection, assets_for_owner


if len(sys.argv) != 2:
    print("Hata: owner gerekli", file=sys.stderr)
    sys.exit(2)

owner = sys.argv[1]
request_id = str(uuid.uuid4())


handler = logging.StreamHandler()

formatter = logging.Formatter(
    "level=%(levelname)s request_id=%(request_id)s "
    "event=%(event)s owner=%(owner)s "
    "row_count=%(row_count)s error_type=%(error_type)s",
    defaults={
        "row_count": "-",
        "error_type": "-"
    }
)

handler.setFormatter(formatter)

logger = logging.getLogger("worker")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logger = logging.LoggerAdapter(
    logger,
    {
        "request_id": request_id,
        "owner": owner
    },
    merge_extra=True
)


# 1 — Request başladı
logger.info(
    "request_started",
    extra={"event": "request_started"}
)


# 2 — Database bağlantısı
logger.info(
    "db_connect_started",
    extra={"event": "db_connect_started"}
)

try:
    connection = get_connection()

except Exception as hata:
    logger.error(
        "db_connect_failed",
        extra={
            "event": "db_connect_failed",
            "error_type": type(hata).__name__
        }
    )
    sys.exit(1)


logger.info(
    "db_connect_ok",
    extra={"event": "db_connect_ok"}
)


# 3 — Query
logger.info(
    "query_started",
    extra={"event": "query_started"}
)

try:
    rows = assets_for_owner(connection, owner)

except Exception as hata:
    logger.error(
        "query_failed",
        extra={
            "event": "query_failed",
            "error_type": type(hata).__name__
        }
    )
    sys.exit(1)

finally:
    connection.close()


logger.info(
    "query_ok",
    extra={
        "event": "query_ok",
        "row_count": len(rows)
    }
)


# 4 — Kullanıcı çıktısı
print(f"owner={owner} assets={len(rows)}")

if rows:
    for hostname, risk in rows:
        print(f"hostname={hostname} risk={risk}")


# 5 — Request tamamlandı
logger.info(
    "request_completed",
    extra={
        "event": "request_completed",
        "row_count": len(rows)
    }
)
