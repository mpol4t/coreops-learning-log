def assets_for_owner(conn, owner_name):
    rows = conn.execute(
        """
        SELECT assets.hostname, assets.risk
        FROM owners
        JOIN assets
        ON assets.owner_id = owners.id
        WHERE owners.name = %s
        ORDER BY assets.hostname
        """,
        (owner_name,),
    ).fetchall()

    return rows
