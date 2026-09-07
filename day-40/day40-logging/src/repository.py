import os

import psycopg


def get_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def assets_for_owner(connection, owner):
    query = """
    SELECT assets.hostname, assets.risk
    FROM assets
    JOIN owners
    ON assets.owner_id = owners.id
    WHERE owners.name = %s
    ORDER BY assets.id;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (owner,))
        return cursor.fetchall()