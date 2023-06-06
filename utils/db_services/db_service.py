import sqlite3


def db_init():
    conn = sqlite3.connect('users_sd_settings.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
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
    conn.commit()
    return conn, cur
