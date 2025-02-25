import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Теперь вы можете получить переменные с помощью os.getenv()
TOKEN = os.getenv("TOKEN")
ADMIN_LIST = os.getenv("ADMIN_LIST")
DATABASE_URL = f"postgresql://{os.getenv("USER_NAME")}:{os.getenv("PASSWORD_PSQL")}@localhost:{os.getenv("PORT")}/{os.getenv("DB_NAME")}"