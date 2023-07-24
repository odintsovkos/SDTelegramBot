"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""


from aiogram.dispatcher.filters.state import StatesGroup, State


class SDStates(StatesGroup):
    waiting_for_authorization = State()
    enter_prompt = State()

    settings = State()
    gen_settings = State()
    settings_set_model = State()
    settings_set_style = State()
    settings_set_lora = State()
    settings_set_n_prompt = State()
    settings_set_sampler = State()
    settings_set_steps = State()
    settings_set_wh = State()
    settings_set_cfg_scale = State()
    settings_set_restore_face = State()
    settings_set_batch_count = State()

    hr_settings = State()
    hr_set_on_off = State()
    hr_change_upscaler = State()
    hr_set_steps = State()
    hr_set_denoising_strength = State()
    hr_set_upscale_by = State()

    ad_settings = State()
    ad_on_off = State()
    ad_change_model = State()
    ad_set_prompt = State()
    ad_set_neg_prompt = State()
    ad_set_confidence = State()
    ad_set_mask_blur = State()
    ad_set_denoising_strength = State()
    ad_set_wh = State()
    ad_set_steps = State()

    other_settings = State()
    enable_auto_translate = State()


    restart_sd = State()


