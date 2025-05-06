import uuid
from sqlalchemy.orm import Session
from model import Studyroom
from sqlalchemy.exc import IntegrityError
from utils import get_dict_from_sqlalchemy
from datetime import time


# 查询studyroom通过id
def get_studyroom_by_id(db: Session, studyroom_id: str):
    return get_dict_from_sqlalchemy(db.query(Studyroom).filter(Studyroom.id == studyroom_id).first())


# 查询studyroom通过room_name
def get_studyroom_by_room_name(db: Session, room_name: str):
    return get_dict_from_sqlalchemy(db.query(Studyroom).filter(Studyroom.room_name == room_name).first())


# 获取所有StudyRoom
def get_all_studyrooms(db: Session):
    return [get_dict_from_sqlalchemy(obj) for obj in db.query(Studyroom).all()]


# 更新StudyRoom
def update_studyroom(db: Session, studyroom_id: str, room_data: dict):
    studyroom = db.query(Studyroom).filter(Studyroom.id == studyroom_id).first()
    if not studyroom:
        return None

    for key, value in room_data.items():
        setattr(studyroom, key, value)

    try:
        db.commit()
        db.refresh(studyroom)
        return get_dict_from_sqlalchemy(studyroom)
    except IntegrityError:
        db.rollback()
        return None


# 插入StudyRoom
def insert_studyroom(db: Session, studyroom_data: dict):
    new_studyroom = Studyroom(
        id=str(uuid.uuid4()).replace("-", ""),
        room_name=studyroom_data["room_name"],
        close_time=studyroom_data["close_time"],
        open_time=studyroom_data["open_time"],
        room_row=studyroom_data["room_row"],
        room_column=studyroom_data["room_column"],
    )

    db.add(new_studyroom)
    try:
        db.commit()
        db.refresh(new_studyroom)
        return get_dict_from_sqlalchemy(new_studyroom)
    except IntegrityError:
        db.rollback()
        return None


# 删除StudyRoom
def delete_studyroom(db: Session, studyroom_id: str):
    studyroom = db.query(Studyroom).filter(Studyroom.id == studyroom_id).first()
    if studyroom:
        db.delete(studyroom)
        db.commit()
        return get_dict_from_sqlalchemy(studyroom)
    return None


# 批量更新所有 StudyRoom 的 open_time 和 close_time
def update_all_studyrooms_time(db: Session, open_time: time, close_time: time):
    try:
        # 使用 `update` 来批量更新
        db.query(Studyroom).update({Studyroom.open_time: open_time, Studyroom.close_time: close_time})
        db.commit()
        # 获取更新后的所有 StudyRoom 信息
        updated_studyrooms = db.query(Studyroom).all()
        return [get_dict_from_sqlalchemy(studyroom) for studyroom in updated_studyrooms]
    except IntegrityError:
        db.rollback()
        return None
