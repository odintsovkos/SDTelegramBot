class SDSettings:
    tg_id: int
    sd_model: str
    sd_style: str
    sd_n_prompt: str
    sd_sampler: str
    sd_steps: int
    sd_width: int
    sd_height: int
    sd_cfg_scale: float
    sd_restore_face: bool
    sd_batch_count: int

    def __init__(self, tg_id, sd_model, sd_style, sd_n_prompt, sd_sampler, sd_steps, sd_wh, sd_cfg_scale, sd_restore_face, sd_batch_count) -> None:
        self.tg_id = tg_id
        self.sd_model = sd_model
        self.sd_style = sd_style
        self.sd_n_prompt = sd_n_prompt
        self.sd_sampler = sd_sampler
        self.sd_steps = sd_steps
        self.sd_width = sd_wh.split('x')[0]
        self.sd_height = sd_wh.split('x')[1]
        self.sd_cfg_scale = sd_cfg_scale
        self.sd_restore_face = sd_restore_face
        self.sd_batch_count = sd_batch_count
