CREATE SCHEMA IF NOT EXISTS stats;

CREATE TABLE IF NOT EXISTS stats.socket (
    name TEXT PRIMARY KEY,
    count BIGINT
);

CREATE TABLE IF NOT EXISTS stats.commands (
    id SERIAL PRIMARY KEY,

    guild BIGINT,
    channel BIGINT,
    author BIGINT,
    used TIMESTAMP,
    prefix TEXT,
    command TEXT,

    failed BOOLEAN
);