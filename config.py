import os
from dotenv import load_dotenv

# Загрука переменных
load_dotenv()

# Получение данных из .env
TOKEN = os.getenv("TOKEN")
API_KEY_LLM = os.getenv("API_KEY_LLM")
ADMIN_LIST = os.getenv("ADMIN_LIST")
DATABASE_URL = f"postgresql://{os.getenv("USER_NAME")}:{os.getenv("PASSWORD_PSQL")}@localhost:{os.getenv("PORT")}/{os.getenv("DB_NAME")}"
