CREATE SCHEMA IF NOT EXISTS users;

CREATE TABLE IF NOT EXISTS users.nicknames (
    id SERIAL PRIMARY KEY,

    guild BIGINT REFERENCES guilds (id) ON DELETE CASCADE,
    member BIGINT,
    nickname TEXT
);

CREATE TABLE IF NOT EXISTS users.usernames (
    id SERIAL PRIMARY KEY,

    snowflake BIGINT,
    username TEXT
);

CREATE TABLE IF NOT EXISTS users.games (
    game TEXT,
    snowflake BIGINT,
    id VARCHAR,
    PRIMARY KEY (game, snowflake)
);

CREATE TABLE IF NOT EXISTS users.interactions (
    method TEXT,
    initiator BIGINT,
    receiver BIGINT,
    count BIGINT DEFAULT 1,
    PRIMARY KEY (method, initiator, receiver)
);

CREATE TABLE IF NOT EXISTS users.totals (
    method TEXT,
    snowflake BIGINT,
    count BIGINT DEFAULT 1,
    PRIMARY KEY (method, snowflake)
);