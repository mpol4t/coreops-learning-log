import psycopg

from src.repository import assets_for_owner


dsn = (
    "postgresql://coreops:coreops-lab"
    "@127.0.0.1:15432/coreops_test"
)

with psycopg.connect(dsn) as conn:
    conn.execute(
        "TRUNCATE TABLE assets, owners RESTART IDENTITY CASCADE"
    )

    owner_row = conn.execute(
        "INSERT INTO owners (name) VALUES (%s) RETURNING id",
        ("test-team",),
    ).fetchone()

    owner_id = owner_row[0]

    conn.execute(
        """
        INSERT INTO assets (hostname, owner_id, risk)
        VALUES (%s, %s, %s)
        """,
        ("alpha.local", owner_id, 80),
    )

    conn.execute(
        """
        INSERT INTO assets (hostname, owner_id, risk)
        VALUES (%s, %s, %s)
        """,
        ("beta.local", owner_id, 20),
    )

    rows = assets_for_owner(conn, "test-team")

    expected = [
        ("alpha.local", 80),
        ("beta.local", 20),
    ]

    assert rows == expected, f"expected={expected}, got={rows}"

print("PASS")
