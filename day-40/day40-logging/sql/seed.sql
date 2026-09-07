INSERT INTO owners (name)
VALUES
    ('blue-team'),
    ('red-team');

INSERT INTO assets (hostname, owner_id, risk)
VALUES
    ('blue-web-01', 1, 20),
    ('blue-db-01', 1, 60),
    ('red-web-01', 2, 40);