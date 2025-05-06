from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from service.seat_service import get_seat_by_id, get_seats_by_studyroom_id, update_seat, delete_seat, insert_seat, \
    get_seats_by_studyroom_id_and_user_booking_time, update_seat_status
from schemas import Response, SeatCreate, SeatUpdate
from database import SessionLocal
from datetime import time

seat_router = APIRouter()


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 通过id查询seat
@seat_router.get("/{seat_id}", response_model=Response)
def get_seat_by_id_route(seat_id: str, db: Session = Depends(get_db)):
    seat = get_seat_by_id(db, seat_id)
    if seat:
        return Response(status=200, message="查找成功", data=seat)
    raise HTTPException(status_code=404, detail="自习室不存在")


# 获取座位列表（按自习室ID查询）
@seat_router.get("/list/{studyroom_id}", response_model=Response)
def get_seats_by_studyroom_id_route(studyroom_id: str, db: Session = Depends(get_db)):
    seats = get_seats_by_studyroom_id(db, studyroom_id)
    if not seats:
        raise HTTPException(status_code=404, detail="座位不存在")
    return Response(status=200, message="查找成功", data=seats)


# 更新座位
@seat_router.put("/{seat_id}", response_model=Response)
def update_seat_router(seat_id: str, seat_data: SeatUpdate, db: Session = Depends(get_db)):
    seat = get_seat_by_id(db, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="座位不存在")

    updated_seat = update_seat(db, seat_id, seat_data.dict())
    if updated_seat:
        return Response(status=200, message="座位状态更新成功", data=updated_seat)
    raise HTTPException(status_code=400, detail="更新失败")


# 签到，更新座位状态为已签到
@seat_router.put("/status/{seat_id}", response_model=Response)
def update_seat_status_router(seat_id: str, status: int, db: Session = Depends(get_db)):
    seat = get_seat_by_id(db, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="座位不存在")

    updated_seat = update_seat_status(db, seat_id, status)
    if updated_seat:
        return Response(status=200, message="座位状态更新成功", data=updated_seat)
    raise HTTPException(status_code=400, detail="更新失败")


# 插入 Seat
@seat_router.post("/", response_model=Response)
def create_seat(seat_data: SeatCreate, db: Session = Depends(get_db)):
    new_seat = insert_seat(db, seat_data.dict())
    if not new_seat:
        raise HTTPException(status_code=400, detail="创建失败")
    return Response(status=200, message="创建成功", data=new_seat)


# 删除 StudyRoom
@seat_router.delete("/{seat_id}", response_model=Response)
def delete_seat_route(seat_id: str, db: Session = Depends(get_db)):
    deleted_seat = delete_seat(db, seat_id)
    if not deleted_seat:
        raise HTTPException(status_code=404, detail="座位不存在")
    return Response(status=200, message="删除成功", data=deleted_seat)


# 查询某room_id自习室的所有某user在期望[begin_time,end_time]可预约的seat
@seat_router.get("/list/available/{studyroom_id}", response_model=Response)
def get_seats_by_studyroom_id_and_user_booking_time_route(studyroom_id: str,
                                                          user_id: int = Query(..., description="用户ID"),
                                                          begin_time: time = Query(..., description="期望预定开始时间"),
                                                          end_time: time = Query(..., description="期望预定结束时间"),
                                                          db: Session = Depends(get_db)):
    seats = get_seats_by_studyroom_id_and_user_booking_time(db, studyroom_id, user_id, begin_time, end_time)
    if not seats:
        raise HTTPException(status_code=404, detail="座位不存在")
    return Response(status=200, message="查找成功", data=seats)
