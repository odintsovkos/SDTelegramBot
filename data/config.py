from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
USERS = env.list("USERS")
IP = env.str("ip")

# Запустить SD при старте бота
launch_sd_at_bot_started = True

# Проверка запуска SD
# False - Проверить и выйти если не запущена SD,
# True - Проверять через каждые time_the_next_check_s секунд, num_of_checks раз.
is_wait_sd_launch = True
time_the_next_check_s = 1

# Со значением 0 будет проверять бесконечно, пока не запустится SD или пользователь не закроет бот.
num_of_checks = 0


sd_path = """D:\PROJECTS\AI\stable-diffusion-webui"""