import aiosqlite

from data.sd_default_params import get_default_params


async def db_create_table():
    async with aiosqlite.connect('users_sd_settings.db') as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users(
           tg_id INT PRIMARY KEY,
           sd_model TEXT,
           sd_style TEXT,
           sd_n_prompt TEXT,
           sd_sampler TEXT,
           sd_steps INT,
           sd_width_height TEXT,
           sd_cfg_scale REAL,
           sd_restore_face INT,
           sd_batch_count INT);
        """)
        await db.commit()


async def db_get_sd_settings(tg_id: int):
    async with aiosqlite.connect('users_sd_settings.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(f"SELECT * FROM users WHERE tg_id={tg_id};") as cursor:
            return await cursor.fetchone()


async def db_get_all_tg_id():
    async with aiosqlite.connect('users_sd_settings.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(f"SELECT tg_id FROM users;") as cursor:
            return await cursor.fetchall()


async def db_delete_user(tg_id):
    async with aiosqlite.connect('users_sd_settings.db') as db:
        async with db.execute(f"DELETE FROM users WHERE tg_id={tg_id};"):
            await db.commit()


async def db_get_sd_setting(tg_id: int, param: str):
    async with aiosqlite.connect('users_sd_settings.db') as db:
        async with db.execute(f"SELECT {param} FROM users WHERE tg_id={tg_id};") as cursor:
            async for row in cursor:
                return row[0]


async def db_set_sd_settings(tg_id, setting, value):
    async with aiosqlite.connect('users_sd_settings.db') as db:
        await db.execute(f"""UPDATE users SET {setting}="{value}" WHERE tg_id={tg_id};""")
        await db.commit()


async def db_create_new_user_settings(tg_id: int):
    params = list(get_default_params(tg_id).values())
    async with aiosqlite.connect('users_sd_settings.db') as db:
        await db.execute(f"""INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", params)
        await db.commit()


async def db_update_default_settings(tg_id: int):
    params = list(get_default_params(tg_id).values())
    settings = ['tg_id', 'sd_model', 'sd_style', 'sd_n_prompt', 'sd_sampler', 'sd_steps', 'sd_width_height',
                'sd_cfg_scale', 'sd_restore_face', 'sd_batch_count']

    for i in range(len(settings) - 1):
        await db_set_sd_settings(tg_id, settings[i], params[i])
