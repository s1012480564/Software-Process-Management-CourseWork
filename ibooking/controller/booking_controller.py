from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from service.booking_service import get_all_bookings_by_user_id, get_all_bookings_by_seat_id, insert_booking, \
    get_all_joint_bookings_by_user_id, delete_booking, push_booking_reminder, check_and_update_booking
from schemas import Response, BookingCreate
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import date, datetime, timedelta
from functools import partial

# 创建路由对象
booking_router = APIRouter()

# 创建调度器
scheduler = AsyncIOScheduler()


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 查找所有 bookings 通过 seat_id
@booking_router.get("/seat/{seat_id}", response_model=Response)
def get_all_bookings_by_seat_id_route(seat_id: str, db: Session = Depends(get_db)):
    bookings = get_all_bookings_by_seat_id(db, seat_id)
    if not bookings:
        raise HTTPException(status_code=404, detail="查找失败")
    return Response(status=200, message="查找成功", data=bookings)


# 查找所有 bookings 通过 user_id
@booking_router.get("/user/{user_id}", response_model=Response)
def get_all_bookings_by_user_id_route(user_id: str, db: Session = Depends(get_db)):
    bookings = get_all_bookings_by_user_id(db, user_id)
    if not bookings:
        raise HTTPException(status_code=404, detail="查找失败")
    return Response(status=200, message="查找成功", data=bookings)


# 联查所有 bookings 通过 user_id（返回 + room_name、seat_name）
@booking_router.get("/user/joint/{user_id}", response_model=Response)
def get_all_joint_bookings_by_user_id_route(user_id: str, db: Session = Depends(get_db)):
    bookings = get_all_joint_bookings_by_user_id(db, user_id)
    if not bookings:
        raise HTTPException(status_code=404, detail="查找失败")
    return Response(status=200, message="查找成功", data=bookings)


# 新建预约
@booking_router.post("/", response_model=Response)
def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db)):
    is_available, data = insert_booking(db, booking_data.dict(), grab=True)
    if not is_available:
        msg = data
        raise HTTPException(status_code=400, detail="预约失败！" + msg)
    booking = data

    booking_id = booking["id"]
    user_id = booking["user_id"]
    seat_id = booking["seat_id"]
    begin_time = booking["begin_time"]
    end_time = booking["end_time"]

    begin_datetime = datetime.combine(date.today(), begin_time)
    end_datetime = datetime.combine(date.today(), end_time)

    # 预约开始前 15 分钟推送提醒。misfire_grace_time 作用同下
    scheduler.add_job(
        partial(push_booking_reminder, booking_id=booking_id, user_id=user_id, seat_id=seat_id, reminder_type=1),
        DateTrigger(run_date=begin_datetime - timedelta(minutes=15)), misfire_grace_time=60)

    # 预约开始时 更新状态
    # 由于设计上放宽卡点预约，整点不论秒钟多少，都能预约上。而设置的整点提醒，因此可能错过定时任务
    # 因此错过时设置 60 秒的延迟，也就是整点的时候，在这个分钟内，都是可以重新完成错过的定时任务的时间范围
    scheduler.add_job(
        partial(check_and_update_booking, booking_id=booking_id, seat_id=seat_id, operation_type=1),
        DateTrigger(run_date=begin_datetime), misfire_grace_time=60)

    # 预约开始后 10 分钟未签到时推送提醒
    scheduler.add_job(
        partial(push_booking_reminder, booking_id=booking_id, user_id=user_id, seat_id=seat_id, reminder_type=2),
        DateTrigger(run_date=begin_datetime + timedelta(minutes=10)))

    # 预约开始后 15 分钟未签到时推送取消预约与违约通知
    scheduler.add_job(
        partial(push_booking_reminder, booking_id=booking_id, user_id=user_id, seat_id=seat_id, reminder_type=3),
        DateTrigger(run_date=begin_datetime + timedelta(minutes=15)))

    # 预约开始后 15 分钟未签到时更新状态
    scheduler.add_job(
        partial(check_and_update_booking, booking_id=booking_id, seat_id=seat_id, operation_type=2),
        DateTrigger(run_date=begin_datetime + timedelta(minutes=15)))

    # 预约结束时 结束提醒
    scheduler.add_job(
        partial(push_booking_reminder, booking_id=booking_id, user_id=user_id, seat_id=seat_id, reminder_type=5),
        DateTrigger(run_date=end_datetime))

    # 预约结束时 更新状态
    scheduler.add_job(
        partial(check_and_update_booking, booking_id=booking_id, seat_id=seat_id, operation_type=3),
        DateTrigger(run_date=end_datetime))

    return Response(status=200, message="预约成功！", data=booking)


# 新建抢位预约
@booking_router.post("/grab", response_model=Response)
def create_booking_grab(booking_data: BookingCreate, db: Session = Depends(get_db)):
    is_available, data = insert_booking(db, booking_data.dict(), grab=True)
    if not is_available:
        msg = data
        raise HTTPException(status_code=400, detail="抢位失败！" + msg)

    booking = data
    booking_id = booking["id"]
    user_id = booking["user_id"]
    seat_id = booking["seat_id"]
    begin_time = booking["begin_time"]
    end_time = booking["end_time"]

    begin_datetime = datetime.combine(date.today(), begin_time)
    end_datetime = datetime.combine(date.today(), end_time)

    # 抢位成功时 更新状态。当然其实对于这个，也可以不设定时任务，直接更新状态即可
    scheduler.add_job(
        partial(check_and_update_booking, booking_id=booking_id, seat_id=seat_id, operation_type=1),
        DateTrigger(run_date=begin_datetime), misfire_grace_time=60)

    # 抢位后 5 分钟未签到时推送取消预约与违约通知
    scheduler.add_job(
        partial(push_booking_reminder, booking_id=booking_id, user_id=user_id, seat_id=seat_id, reminder_type=4),
        DateTrigger(run_date=begin_datetime + timedelta(minutes=5)))

    # 抢位后 5 分钟未签到时更新状态
    scheduler.add_job(
        partial(check_and_update_booking, booking_id=booking_id, seat_id=seat_id, operation_type=2),
        DateTrigger(run_date=begin_datetime + timedelta(minutes=5)))

    # 预约结束时 结束提醒
    scheduler.add_job(
        partial(push_booking_reminder, booking_id=booking_id, user_id=user_id, seat_id=seat_id, reminder_type=5),
        DateTrigger(run_date=end_datetime))

    # 预约结束时 更新状态
    scheduler.add_job(
        partial(check_and_update_booking, booking_id=booking_id, seat_id=seat_id, operation_type=3),
        DateTrigger(run_date=end_datetime))

    return Response(status=200, message="抢位成功！", data=booking)


# 删除 booking（取消预约/删除记录）
@booking_router.delete("/{booking_id}", response_model=Response)
def delete_booking_route(booking_id: str, db: Session = Depends(get_db)):
    booking = delete_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="取消失败")
    return Response(status=200, message="取消成功")
