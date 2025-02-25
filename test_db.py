import psycopg2

# Данные для подключения
DATABASE_URL = "postgresql://postgres:Q5I8N_mQt0D4vx_@localhost:5432/calendar_bot"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Успешное подключение к базе данных!")
    conn.close()
except Exception as e:
    print("❌ Ошибка подключения:", e)
