# True сохраняет сгенерированные файлы в папку "outputs/txt2img-images"
from utils.sd_api import api_service

save_files = False

# Путь к папке для сохраненный изображений. Пример: "outputs/txt2img-images"
output_folder = 'outputs/txt2img-images'


# Параметры по умолчанию
def get_default_params(tg_id):
    model = api_service.get_models_sd_api()
    params = {"user_id": tg_id,
              "model_name": model[0]['model_name'],
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
