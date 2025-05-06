import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from model import Seat
from utils import get_dict_from_sqlalchemy
from datetime import time
from service.booking_service import _check_booking_available


# 查询seat通过id
def get_seat_by_id(db: Session, seat_id: str):
    return get_dict_from_sqlalchemy(db.query(Seat).filter(Seat.id == seat_id).first())


# 查询seat通过seat_name
def get_seat_by_name(db: Session, seat_name: str):
    return get_dict_from_sqlalchemy(db.query(Seat).filter(Seat.seat_name == seat_name).first())


# 查询某room_id自习室的所有seat
def get_seats_by_studyroom_id(db: Session, studyroom_id: str):
    return [get_dict_from_sqlalchemy(obj) for obj in db.query(Seat).filter(Seat.studyroom_id == studyroom_id).all()]


# 更新seat信息
def update_seat(db: Session, seat_id: str, room_data: dict):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if not seat:
        return None

    for key, value in room_data.items():
        setattr(seat, key, value)

    try:
        db.commit()
        db.refresh(seat)
        return get_dict_from_sqlalchemy(seat)
    except IntegrityError:
        db.rollback()
        return None


# 更新seat状态
def update_seat_status(db: Session, seat_id: str, status: int):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if not seat:
        return None
    seat.status = status
    try:
        db.commit()
        db.refresh(seat)
        return get_dict_from_sqlalchemy(seat)
    except IntegrityError:
        db.rollback()
        return None


# 为新自习室批量插入全部seat
def insert_all_seats_by_studyroom_id(db: Session, studyroom_id: str, row_num: int, column_num: int):
    seats = []
    try:
        for row in range(1, row_num + 1):
            for column in range(1, column_num + 1):
                seat = Seat(
                    id=str(uuid.uuid4()).replace("-", ""),
                    studyroom_id=studyroom_id,
                    seat_name=f"R{row}C{column}",  # name 规则 R{row}C{column}
                    position_row=row,
                    position_column=column,
                    status=1  # 默认状态为 1，未占用
                )
                db.add(seat)
                seats.append(get_dict_from_sqlalchemy(seat))
        db.commit()
        return seats
    except IntegrityError:
        db.rollback()  # 出错时回滚
        return None


# 插入新seat
def insert_seat(db: Session, seat_data: dict):
    db_seat = Seat(
        id=str(uuid.uuid4()).replace("-", ""),
        studyroom_id=seat_data["studyroom_id"],
        seat_name=seat_data["seat_name"],
        position_row=seat_data["position_row"],
        position_column=seat_data["position_column"],
        status=1  # 默认状态为 1，未占用
    )
    try:
        db.add(db_seat)
        db.commit()
        db.refresh(db_seat)
        return get_dict_from_sqlalchemy(db_seat)
    except IntegrityError:
        db.rollback()
        return None


# 删除seat
def delete_seat(db: Session, seat_id: str):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if seat:
        db.delete(seat)
        db.commit()
        return get_dict_from_sqlalchemy(seat)
    return None


# 查询某room_id自习室的所有某user在期望[begin_time,end_time]可预约的seat
def get_seats_by_studyroom_id_and_user_booking_time(db: Session, studyroom_id: str, user_id: int, begin_time: time,
                                                    end_time: time):
    seats = db.query(Seat).filter(Seat.studyroom_id == studyroom_id).all()
    available_seats = []
    for seat in seats:
        booking_data = {
            "user_id": user_id,
            "seat_id": seat.id,
            "begin_time": begin_time,
            "end_time": end_time
        }
        is_available, _ = _check_booking_available(db, booking_data)
        if is_available:
            available_seats.append(get_dict_from_sqlalchemy(seat))

    return available_seats
