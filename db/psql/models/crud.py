from db.psql.models.models import User, SessionFactory

# Проверка нахождения пользователя в БД
class UserChecker:
    
    def __init__(self, tg_id: int):
        self.tg_id = tg_id
        self.session = SessionFactory()  # Используем SessionFactory для создания сессии

    # Проверка, существует ли пользователь с данным tg_id
    def user_exists(self):
        user = self.session.query(User).filter(User.tg_id == self.tg_id).first()
        return user is not None

    def close(self):
        self.session.close()