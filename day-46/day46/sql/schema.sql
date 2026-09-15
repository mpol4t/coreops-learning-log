CREATE TABLE owners ( 
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE assets(
    id SERIAL PRIMARY KEY,
    hostname TEXT NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES owners(id),
    risk INTEGER NOT NULL
);
