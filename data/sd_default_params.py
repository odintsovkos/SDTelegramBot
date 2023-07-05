# True сохраняет сгенерированные файлы в папку "outputs/txt2img-images"
save_files = False


# Параметры по умолчанию
def get_default_params(tg_id):
    params = {"user_id": tg_id,
              "model_name": 'REAL--\deliberate_v2.safetensors [9aba26abdf]',
              "styles_list": '',
              "lora_list": '',
              "negative_prompt": '(deformed, distorted, disfigured:1.3),poorly drawn,bad anatomy,wrong anatomy,'
                                 'extra limb,missing limb,'
                                 'floating limbs,(mutated hands and fingers:1.4),disconnected limbs,mutation,mutated,'
                                 'ugly,disgusting,'
                                 'blurry,amputation',
              "sampler_name": 'Euler a',
              "steps": 22,
              "width_height": '640x640',
              "cfg_scale": '7.0',
              "restore_face": 1,
              "batch_count": 1}

    return params
