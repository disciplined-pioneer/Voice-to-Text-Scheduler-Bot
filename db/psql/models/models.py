from config import DATABASE_URL

from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey


# Настройка SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)

# Модель пользователя
class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    key_calendar = Column(String, unique=True, nullable=False)

    # Связь с событиями
    events = relationship("Event", back_populates="user")

# Модель события
class Event(Base):

    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, ForeignKey('users.tg_id', ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    alerts = Column(Integer, nullable=False, default=30)

    # Обратная связь с пользователем
    user = relationship("User", back_populates="events")

# Создание таблиц в базе данных
Base.metadata.create_all(engine)
