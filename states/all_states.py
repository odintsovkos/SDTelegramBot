from aiogram.dispatcher.filters.state import StatesGroup, State


class SDStates(StatesGroup):
    enter_prompt = State()
    settings = State()
    settings_set_model = State()
    settings_set_style = State()
    settings_set_n_prompt = State()
    settings_set_sampler = State()
    settings_set_steps = State()
    settings_set_wh = State()
    settings_set_cfg_scale = State()
    settings_set_restore_face = State()
    settings_set_batch_count = State()

