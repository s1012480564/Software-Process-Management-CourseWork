from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.orm import declarative_base
from model import User, Seat

Base = declarative_base()


class Booking(Base):
    __tablename__ = 'booking'

    id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=True)
    seat_id = Column(String(255), ForeignKey(Seat.id, ondelete='CASCADE'), nullable=True)
    begin_time = Column(Time, nullable=True)  # 预订开始时间
    end_time = Column(Time, nullable=True)  # 预订结束时间
    alive = Column(Integer, nullable=True)  # 0 已过期，1 未过期
