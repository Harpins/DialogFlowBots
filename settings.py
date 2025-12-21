import environs

env = environs.Env()
env.read_env()

TG_BOT_TOKEN = env.str("TG_BOT_TOKEN")
PROJECT_ID = env.str("PROJECT_ID")
JSON_PATH = env.str("JSON_PATH")
LANGUAGE_CODE = "ru-RU"
VK_GROUP_TOKEN = env.str("VK_GROUP_TOKEN")
