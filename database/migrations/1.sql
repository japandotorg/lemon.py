create type mod as enum ('warn', 'glitch');

create table if not exists mod
(
    id       serial primary key,
    user_id  bigint,
    mod_id   bigint,
    type     mod,
    reason   text,
    created  timestamp not null default (current_timestamp at time zone 'utc')
);

insert info (schema_version) values (1);