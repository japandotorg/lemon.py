from asyncpg import Connection, Pool, Record

__all__ = ("CustomPool", "create_pool")


class CustomPool(Pool):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.cache = {}
        self.calls = {
            "EXECUTE": 0,
            "EXECUTEMANY": 0,
            "FETCH": 0,
            "FETCHVAL": 0,
            "FETCHROW": 0,
        }

    async def execute(self, query: str, *args, timeout: float = None) -> str:
        self.calls["EXECUTE"] += 1
        async with self.acquire() as con:
            return await con.execute(query, *args, timeout=timeout)

    async def executemany(self, command: str, args, *, timeout: float = None):
        self.calls["EXECUTEMANY"] += 1
        async with self.acquire() as con:
            return await con.executemany(command, args, timeout=timeout)

    async def fetch(self, query, *args, timeout=None) -> list:
        self.calls["FETCH"] += 1
        async with self.acquire() as con:
            return await con.fetch(query, *args, timeout=timeout)

    async def fetchval(self, query, *args, column=0, timeout=None):
        self.calls["FETCHVAL"] += 1
        async with self.acquire() as con:
            return await con.fetchval(query, *args, column=column, timeout=timeout)

    async def fetchrow(self, query, *args, timeout=None):
        self.calls["FETCHROW"] += 1
        async with self.acquire() as con:
            return await con.fetchrow(query, *args, timeout=timeout)

    async def register_user(self, game: str, snowflake: int, _id: str):
        query = """
            INSERT INTO
                games
            VALUES
                ($1, $2, $3)
            ON CONFLICT (game, snowflake)
                DO UPDATE
                    SET
                        id = $3
            """
        await self.execute(query, game, snowflake, _id)

    async def command_insert(self, data: str):
        query = """
            INSERT INTO
                commands (guild, channel, author, used, prefix, command, failed)
            SELECT x.guild, x.channel, x.author, x.used, x.prefix, x.command, x.failed
                   FROM JSONB_TO_RECORDSET($1::jsonb) AS
                   x(
                        guild BIGINT,
                        channel BIGINT,
                        author BIGINT,
                        used TIMESTAMP,
                        prefix TEXT,
                        command TEXT,
                        failed BOOLEAN
                )
            """
        await self.execute(query, data)


def create_pool(
    bot,
    dsn=None,
    *,
    min_size=10,
    max_size=10,
    max_queries=50000,
    max_inactive_connection_lifetime=300.0,
    setup=None,
    init=None,
    loop=None,
    connection_class=Connection,
    record_class=Record,
    **connect_kwargs,
) -> CustomPool:
    return CustomPool(
        bot,
        dsn,
        connection_class=connection_class,
        record_class=record_class,
        min_size=min_size,
        max_size=max_size,
        max_queries=max_queries,
        loop=loop,
        setup=setup,
        init=init,
        max_inactive_connection_lifetime=max_inactive_connection_lifetime,
        **connect_kwargs,
    )