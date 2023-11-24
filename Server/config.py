from environs import Env

env = Env()
env.read_env()

host = env.str("HOST", "localhost")
port = env.int("PORT", default=5005)

db_host = env.str("DB_HOST")
db_port = env.int("DB_PORT")
db_user = env.str("DB_USER")
db_password = env.str("DB_PASSWORD")
db_name = env.str("DB_NAME")

PATH_TO_IMAGE = env.str("PATH_TO_IMAGE")
barrier_is_opened = False
ai_is_enabled = True
