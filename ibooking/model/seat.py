from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base
from model import Studyroom

Base = declarative_base()


class Seat(Base):
    # 行列号就不做检查了，有没有在教室行列数范围内，需求也不是那么确定的，也懒得弄了，宽松处理
    __tablename__ = 'seat'
    id = Column(String(255), primary_key=True, nullable=True)
    studyroom_id = Column(String(255), ForeignKey(Studyroom.id, ondelete='CASCADE'), nullable=True)
    seat_name = Column(String(255), nullable=True, unique=True)
    position_row = Column(Integer, nullable=True)
    position_column = Column(Integer, nullable=True)
    status = Column(Integer, nullable=True)  # 当前座位状态。未占用 1, 已占用 2, 已签到 3

    __table_args__ = (
        UniqueConstraint("position_row", "position_column", name='position'),
    )
