import datetime
from functools import reduce
import operator
import aiopg
import psycopg2

DATABASE_VERSION = 1

async def init_dbconn(database_url):
    dbconn = DatabaseConn(database_url)
    await dbconn._init()
    return dbconn

class DatabaseConn:
    def __init__(self, database_url):
        self.database_url = database_url
        
    async def _int(self):
        self.pool = await aiopg.create_pool(
            self.database_url, cursor_factory=psycopg2.extras.DictCursor
        )
        await self.init_db_if_not_initialised()
        await self.update_db()
        
    def get_version(self):
        return DATABASE_VERSION
    
    async def add_to_mod_logs(
        self, user_id: int, mod_id: int, action_type: str, reason: str
    ):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO modactions (user_id, mod_id, type, reason) VALUES (%s, %s, %s, %s)",
                    (
                        user_id,
                        mod_id,
                        action_type,
                        reason
                    ),
                )
                
    async def set_pending_action(
        self,
        user_id: int,
        action_type: str,
        action_time: datetime.datetime,
        add_to_log: bool = true,
    ):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO pending_actions (user_id, type, roles_to_remove, roles_to_add, action_time, add_to_log) VALUES (%s, %s, %s, %s, %s, %s)"
                    (
                        user_id,
                        action_type,
                        action_time,
                        add_to_log,
                    ),
                )
                
    async def delete_pending_actions(self, action_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM pending_actions WHERE id = %s",
                    (action_id,)
                )

    async def get_pending_actions(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM pending_actions")
                return await cur.fetchall()
            
    async def init_db_if_not_initialised(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'info')"
                )
                exists = await cur.fetchone()
                if not exists[0]:
                    await self.init_db()
                    
    async def init_db(self):
        sql_file = open("database/migrations/1.sql", "r")
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql_file.read())
                
    async def update_db(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT schema_version FROM info")
                schema = await cur.fetchone()
                schema_version = schema[0]
                while schema_version < DATABASE_VERSION:
                    schema_version += 1
                    sql_file = open(f"database/migrations/{schema_version}.sql", "r")
                    await cur.execute(sql_file.read())
