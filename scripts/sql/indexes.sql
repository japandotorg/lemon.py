CREATE INDEX IF NOT EXISTS id_guild ON public.guilds (id);

CREATE INDEX IF NOT EXISTS game_user_games ON users.games (game, snowflake);

CREATE INDEX IF NOT EXISTS timer_expires ON events.timers (expires);

CREATE INDEX IF NOT EXISTS guild_command ON stats.commands (guild);
CREATE INDEX IF NOT EXISTS user_command ON stats.commands (author);