CREATE TABLE owners (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text UNIQUE NOT NULL
);

CREATE TABLE assets (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hostname text UNIQUE NOT NULL,
    owner_id bigint NOT NULL REFERENCES owners(id),
    risk integer NOT NULL CHECK (risk BETWEEN 0 AND 100)
);
