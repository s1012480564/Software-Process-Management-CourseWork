from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Studyroom(Base):
    __tablename__ = 'studyroom'
    id = Column(String(255), primary_key=True, nullable=True)
    room_name = Column(String(255), nullable=True, unique=True)
    room_row = Column(Integer, nullable=True)
    room_column = Column(Integer, nullable=True)
    open_time = Column(Time, nullable=True)
    close_time = Column(Time, nullable=True)
