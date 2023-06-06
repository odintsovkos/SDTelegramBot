from loader import db_conn, db_cur


def db_set_sd_settings(tg_id, setting, value):
    db_cur.execute(f"""UPDATE users SET {setting}="{value}" WHERE tg_id={tg_id};""")
    db_conn.commit()


def db_create_new_user_settings(tg_id: int):
    params = (tg_id,
              'REAL--\deliberate_v2.safetensors [9aba26abdf]',
              '',
              '(deformed, distorted, disfigured:1.3),poorly drawn,bad anatomy,wrong anatomy,extra limb,missing limb,'
              'floating limbs,(mutated hands and fingers:1.4),disconnected limbs,mutation,mutated,ugly,disgusting,'
              'blurry,amputation', 'Euler a', 22, '640x640', '7.0', 1, 1)
    db_cur.execute(f"""INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", params)
    db_conn.commit()


def db_update_default_settings(tg_id: int):
    params = (tg_id,
              'REAL--\deliberate_v2.safetensors [9aba26abdf]',
              '',
              '(deformed, distorted, disfigured:1.3),poorly drawn,bad anatomy,wrong anatomy,extra limb,missing limb,'
              'floating limbs,(mutated hands and fingers:1.4),disconnected limbs,mutation,mutated,ugly,disgusting,'
              'blurry,amputation', 'Euler a', 22, '640x640', '7.0', 1, 1)

    settings = ['tg_id', 'sd_model', 'sd_style', 'sd_n_prompt', 'sd_sampler', 'sd_steps', 'sd_width_height', 'sd_cfg_scale', 'sd_restore_face', 'sd_batch_count']

    for i in range(len(settings) - 1):
        db_set_sd_settings(tg_id, settings[i], params[i])
