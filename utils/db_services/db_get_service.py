from loader import db_cur


def db_get_sd_settings(tg_id: int):
    db_cur.execute(f"SELECT * FROM users WHERE tg_id={tg_id};")
    result = db_cur.fetchone()
    return result


def db_get_sd_setting(tg_id: int, param: str):
    db_cur.execute(f"SELECT {param} FROM users WHERE tg_id={tg_id};")
    result = db_cur.fetchone()
    return ''.join(result)
