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
    "level=%(levelname)s request_id=%(request_id)s event=%(event)s owner=%(owner)s row_count=%(row_count)s error_type=%(error_type)s",
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


logger.info(
    "request_started",
    extra={"event": "request_started"}
)

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

try:
    logger.info(
        "db_query_started",
        extra={"event": "db_query_started"}
    )

    rows = assets_for_owner(connection, owner)

    logger.info(
        "db_query_ok",
        extra={
            "event": "db_query_ok",
            "row_count": len(rows)
        }
    )

except Exception as hata:
    logger.error(
        "db_query_failed",
        extra={
            "event": "db_query_failed",
            "error_type": type(hata).__name__
        }
    )
    sys.exit(1)

finally:
    connection.close()

logger.info(
    "request_completed",
    extra={"event": "request_completed"}
)
