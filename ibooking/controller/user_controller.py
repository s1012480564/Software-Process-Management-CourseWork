from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas import UserBase, UserCreate, UserUpdate, Response
from database import SessionLocal
from service.user_service import get_user_by_stu_no, get_user_by_username, get_all_users, create_user, \
    update_user_password, delete_user, login_user

user_router = APIRouter()


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 获取用户列表（分页）
@user_router.get("/list/{page_num}", response_model=Response)
def list_users(page_num: int, db: Session = Depends(get_db)):
    users = get_all_users(db, page_num)
    return Response(status=200, message="查询成功", data=users)


# 通过用户名查询用户
@user_router.get("/{username}", response_model=Response)
def get_user_by_username_route(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if user:
        return Response(status=200, message="查找成功", data=user)
    raise HTTPException(status_code=404, detail="用户未找到")


# 用户注册
@user_router.post("/register", response_model=Response)
def insert_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 先检查用户名和学号是否已存在
    if get_user_by_username(db, user_data.username) or get_user_by_stu_no(db, user_data.stu_no):
        raise HTTPException(status_code=400, detail="用户名或学号已被使用")

    new_user = create_user(db, user_data)
    if new_user:
        return Response(status=200, message="注册成功", data=new_user)
    raise HTTPException(status_code=400, detail="注册失败，数据库插入错误")


# 用户登录
@user_router.post("/login", response_model=Response)
def login(user_data: UserBase, db: Session = Depends(get_db)):
    user = login_user(db, user_data.username, user_data.password)
    if user:
        return Response(status=200, message="登录成功", data=user)
    raise HTTPException(status_code=400, detail="用户名或密码错误")


# 删除用户
@user_router.delete("/delete/{user_id}", response_model=Response)
def delete_user_route(user_id: str, db: Session = Depends(get_db)):
    deleted_user = delete_user(db, user_id)
    if deleted_user:
        return Response(status=200, message="删除成功", data=deleted_user)
    raise HTTPException(status_code=404, detail="用户未找到")


# 更新用户密码信息
@user_router.put("/update", response_model=Response)
def update_user_route(user_id: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    updated_user = update_user_password(db, user_id, user_data)
    if updated_user:
        if updated_user == -1:
            raise HTTPException(status_code=400, detail="原密码错误")
        return Response(status=200, message="更新成功", data=updated_user)
    raise HTTPException(status_code=404, detail="用户未找到")
