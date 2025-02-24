import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Теперь вы можете получить переменные с помощью os.getenv()
TOKEN = os.getenv("TOKEN")
ADMIN_LIST = os.getenv("ADMIN_LIST")
