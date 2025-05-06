from sqlalchemy.orm import Session
from uuid import uuid4
from model import Booking, Seat, User, Studyroom
from sqlalchemy.exc import IntegrityError
from utils import get_dict_from_sqlalchemy
from datetime import datetime
from database import SessionLocal

# 用户消息
user_messages = {}


async def add_user_messages(user_id: int, message: str):
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(message)


# 由于异步任务和数据库会话冲突的问题，不能对数据库连接使用 FastAPI 依赖注入，于是直接在这个函数里手动创建数据库连接
# 定时推送预约提醒
async def push_booking_reminder(booking_id: str, user_id: int, seat_id: str, reminder_type: int):
    '''
    reminder_type:
        1：预约开始前 15 分钟
        2：预约开始后 10 分钟
        3：预约开始后 15 分钟
        4：抢位后 5 分钟
        5：预约(含抢位)结束时
    '''
    db: Session = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:  # 预约不存在或已被取消，则不再推送提醒。其实更加合理的做法是记录 job id，然后移除对应定时任务，这里只是个粗糙的处理
            return None
        if reminder_type == 1:  # 预约开始前 15 分钟
            await add_user_messages(user_id, f"您的预约将在15分钟后开始，请及时到达座位并进行签到。")
        elif reminder_type == 5:  # 预约结束时
            await add_user_messages(user_id, f"您预约的自习时段已结束，感谢您的使用！")
        else:
            seat = db.query(Seat).filter(Seat.id == seat_id).first()
            if not seat:
                return None
            if seat.status == 3:  # 已签到
                return None
            if reminder_type == 2:  # 预约开始后 10 分钟
                await add_user_messages(user_id,
                                        f"您的预约已经开始10分钟，请尽快签到！5分钟后仍未签到，系统将自动取消预约并记录违约！")
            elif reminder_type == 3:  # 预约开始后 15 分钟
                await add_user_messages(user_id, f"您未在规定时间内完成签到，系统已自动取消预约并记录违约！")
            elif reminder_type == 4:  # 抢位后 5 分钟
                await add_user_messages(user_id, f"您未在规定时间内完成签到，系统已自动取消抢位并记录违约！")
    finally:
        db.close()


# 检查 booking 部分相关状态并进行更新
def check_and_update_booking(booking_id: str, seat_id: str, operation_type: int):
    '''
    operation_type:
        1：预约(含抢位)开始时
        2：预约开始后 15 分钟或抢位后 5 分钟
        3：预约(含抢位)结束时
    '''
    db: Session = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:  # 预约不存在或已被取消，则不再通过此函数检查与更新。同上，其实更加合理的做法是记录 job id，然后移除对应定时任务，这里只是个粗糙的处理
            return None
        if operation_type == 1:  # 预约开始时
            update_seat_to_occupied(db, seat_id)
        elif operation_type == 2:  # 预约开始后 15 分钟或抢位后 5 分钟
            seat = db.query(Seat).filter(Seat.id == seat_id).first()
            if not seat:
                return None
            if seat.status == 3:  # 已签到
                return None
            update_seat_to_available(db, seat_id)
            delete_booking(db, booking_id)
        elif operation_type == 3:  # 预约结束时
            update_seat_to_available(db, seat_id)
            update_booking_to_not_alive(db, booking_id)
    finally:
        db.close()


# 查找全部 booking 通过 seat_id
def get_all_bookings_by_seat_id(db: Session, seat_id: str):
    return [get_dict_from_sqlalchemy(obj) for obj in db.query(Booking).filter(Booking.seat_id == seat_id).all()]


# 查找全部 booking 通过 user_id
def get_all_bookings_by_user_id(db: Session, user_id: str):
    return [get_dict_from_sqlalchemy(obj) for obj in db.query(Booking).filter(Booking.user_id == user_id).all()]


# 联查全部 booking 通过 user_id（返回 + room_name、seat_name）
def get_all_joint_bookings_by_user_id(db: Session, user_id: str):
    results = db.query(Booking, Seat, Studyroom) \
        .join(Seat, Seat.id == Booking.seat_id) \
        .join(Studyroom, Studyroom.id == Seat.studyroom_id) \
        .filter(Booking.user_id == user_id) \
        .all()
    bookings = []
    for result in results:
        booking, seat, studyroom = result
        booking_dict = get_dict_from_sqlalchemy(booking)
        booking_dict['seat_name'] = seat.seat_name
        booking_dict['room_name'] = studyroom.room_name
        bookings.append(booking_dict)
    return bookings


# 检查区间 (a, b) 和 (c, d) 是否有重合
def _is_overlap(a, b, c, d):
    # 如果 (a, b) 完全在 (c, d) 的左侧或者完全在 (c, d) 的右侧，则没有重合。否则重合
    if b <= c or a >= d:
        return False
    return True


# 检查区间 [a, b] 是否 [c, d] 的子区间
def _is_subinterval(a, b, c, d):
    # 如果 a >= c 且 b <= d，则 [a, b] 是 [c, d] 的子区间
    if a >= c and b <= d:
        return True
    return False


def _check_booking_available(db: Session, booking_data: dict):
    user = db.query(User).filter(User.id == booking_data["user_id"]).first()
    seat = db.query(Seat).filter(Seat.id == booking_data["seat_id"]).first()
    studyroom = db.query(Studyroom).filter(Studyroom.id == seat.studyroom_id).first()

    # 检查用户是否存在
    if not user:
        return False, "用户不存在"

    # 检查座位是否存在
    if not seat:
        return False, "座位不存在"

    booking_begin_time = booking_data["begin_time"]
    booking_end_time = booking_data["end_time"]
    studyroom_open_time = studyroom.open_time
    studyroom_close_time = studyroom.close_time

    # 检查预约时段该座位所在自习室是否开放
    if not _is_subinterval(booking_begin_time, booking_end_time, studyroom_open_time, studyroom_close_time):
        return False, "该预约时段当前自习室未开放"

    # 检查预约时段该用户是否已有其他预约
    bookings = db.query(Booking).filter(Booking.user_id == booking_data["user_id"], Booking.alive == 1).all()
    for other_booking in bookings:
        other_booking_begin_time = other_booking.begin_time
        other_booking_end_time = other_booking.end_time
        if _is_overlap(booking_begin_time, booking_end_time, other_booking_begin_time, other_booking_end_time):
            return False, "该预约时段您已有其他预约"

    # 检查预约时段该座位是否已被其他用户预约
    bookings = db.query(Booking).filter(Booking.seat_id == booking_data["seat_id"], Booking.alive == 1).all()
    for other_booking in bookings:
        other_booking_begin_time = other_booking.begin_time
        other_booking_end_time = other_booking.end_time
        if _is_overlap(booking_begin_time, booking_end_time, other_booking_begin_time, other_booking_end_time):
            return False, "该时段该座位已被预约"

    # 检查预约开始时间不能早于当前系统时间（抢位可以）
    if booking_begin_time < datetime.now().time().replace(second=0, microsecond=0):
        return False, "预约开始时间不能早于当前系统时间"

    return True, ""


# 插入新的 booking
def insert_booking(db: Session, booking_data: dict, grab):
    # 检查 booking 是否可用
    is_available, msg = _check_booking_available(db, booking_data)

    if not is_available:
        return is_available, msg

    # 创建新的预约
    new_booking = Booking(
        id=str(uuid4()).replace("-", ""),
        user_id=booking_data["user_id"],
        seat_id=booking_data["seat_id"],
        begin_time=booking_data["begin_time"],
        end_time=booking_data["end_time"],
        alive=1  # 设置为未过期
    )

    db.add(new_booking)
    try:
        db.commit()
        db.refresh(new_booking)
        return is_available, get_dict_from_sqlalchemy(new_booking)
    except IntegrityError:
        db.rollback()
        return None, None


# 删除 booking（取消预约/删除记录）
def delete_booking(db: Session, booking_id: str):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        if booking.alive == 1: # 取消预约，座位状态恢复未占用
            update_seat_to_available(db, str(booking.seat_id))
        db.delete(booking)
        db.commit()
        return get_dict_from_sqlalchemy(booking)
    return None


# 更新 booking 为 not alive 的过期状态
def update_booking_to_not_alive(db: Session, booking_id: str):
    booking = db.query(Booking).filter(Booking.user_id == booking_id).first()
    if booking:
        booking.alive = 0
        db.commit()
        return get_dict_from_sqlalchemy(booking)
    return None


# 更新 seat 为 status = 1 的空闲状态
def update_seat_to_available(db: Session, seat_id: str):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if seat:
        seat.status = 1
        db.commit()
        return get_dict_from_sqlalchemy(seat)
    return None


# 更新 seat 为 status = 2 的已占用状态
def update_seat_to_occupied(db: Session, seat_id: str):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if seat:
        seat.status = 2
        db.commit()
        return get_dict_from_sqlalchemy(seat)
    return None


# 签到。更新 seat 为 status = 3 的签到状态
def update_seat_to_signed(db: Session, seat_id: str):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if seat:
        seat.status = 3
        db.commit()
        return get_dict_from_sqlalchemy(seat)
    return None
