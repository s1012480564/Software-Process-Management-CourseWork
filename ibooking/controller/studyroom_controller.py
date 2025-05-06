from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from service.studyroom_service import get_all_studyrooms, get_studyroom_by_id, get_studyroom_by_room_name, \
    update_studyroom, insert_studyroom, delete_studyroom, update_all_studyrooms_time
from service.seat_service import insert_all_seats_by_studyroom_id
from database import SessionLocal
from schemas import Response, StudyroomCreate, StudyroomUpdate, StudyroomTimeBase

studyroom_router = APIRouter()


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 获取所有 StudyRoom
@studyroom_router.get("/list", response_model=Response)
def get_studyrooms(db: Session = Depends(get_db)):
    studyrooms = get_all_studyrooms(db)
    if not studyrooms:
        raise HTTPException(status_code=404, detail="自习室不存在")
    return Response(status=200, message="查找成功", data=studyrooms)


# 通过id查询studyroom
@studyroom_router.get("/{studyroom_id}", response_model=Response)
def get_studyroom_by_id_route(studyroom_id: str, db: Session = Depends(get_db)):
    studyroom = get_studyroom_by_id(db, studyroom_id)
    if studyroom:
        return Response(status=200, message="查找成功", data=studyroom)
    raise HTTPException(status_code=404, detail="自习室不存在")


# 通过room_name查询studyroom
@studyroom_router.get("/{room_name}", response_model=Response)
def get_studyroom_by_room_name_route(room_name: str, db: Session = Depends(get_db)):
    studyroom = get_studyroom_by_room_name(db, room_name)
    if studyroom:
        return Response(status=200, message="查找成功", data=studyroom)
    raise HTTPException(status_code=404, detail="自习室不存在")


# 更新 StudyRoom
@studyroom_router.put("/{studyroom_id}", response_model=Response)
def update_studyroom_route(studyroom_id: str, studyroom_data: StudyroomUpdate, db: Session = Depends(get_db)):
    updated_room = update_studyroom(db, studyroom_id, studyroom_data.dict())
    if not updated_room:
        raise HTTPException(status_code=404, detail="自习室不存在")
    return Response(status=200, message="更新成功", data=updated_room)


# 插入 StudyRoom
@studyroom_router.post("/", response_model=Response)
def create_studyroom(studyroom_data: StudyroomCreate, db: Session = Depends(get_db)):
    new_room = insert_studyroom(db, studyroom_data.dict())
    if not new_room:
        raise HTTPException(status_code=400, detail="创建失败")
    seats = insert_all_seats_by_studyroom_id(db, new_room["id"], new_room["room_row"], new_room["room_column"])
    if not seats:  # 这里设计，座位创建失败的话，允许自习室创出来的。管理员根据需求手动删除自习室重创，或者手动创建座位
        raise HTTPException(status_code=400, detail="创建失败")
    return Response(status=200, message="创建成功", data=new_room)


# 删除 StudyRoom
@studyroom_router.delete("/{studyroom_id}", response_model=Response)
def delete_studyroom_route(studyroom_id: str, db: Session = Depends(get_db)):
    deleted_room = delete_studyroom(db, studyroom_id)
    if not deleted_room:
        raise HTTPException(status_code=404, detail="自习室不存在")
    return Response(status=200, message="删除成功", data=deleted_room)


# 批量更新所有 StudyRoom 的 open_time 和 close_time
@studyroom_router.post("/update_all_time", response_model=Response)
def update_all_studyrooms_time_route(timestamp: StudyroomTimeBase, db: Session = Depends(get_db)):
    open_time = timestamp.open_time
    close_time = timestamp.close_time
    updated_studyrooms = update_all_studyrooms_time(db, open_time, close_time)
    if not updated_studyrooms:
        raise HTTPException(status_code=400, detail="更新失败")
    return Response(status=200, message="更新成功", data=updated_studyrooms)
