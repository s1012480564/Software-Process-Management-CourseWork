from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from model import User
from schemas import UserCreate, UserUpdate
from utils import get_dict_from_sqlalchemy


# 查询用户通过用户名
def get_user_by_username(db: Session, username: str):
    return get_dict_from_sqlalchemy(db.query(User).filter(User.username == username).first())


# 查询用户通过学号
def get_user_by_stu_no(db: Session, stu_no: str):
    return get_dict_from_sqlalchemy(db.query(User).filter(User.stu_no == stu_no).first())


# 查询用户通过ID
def get_user_by_id(db: Session, user_id: str):
    return get_dict_from_sqlalchemy(db.query(User).filter(User.id == user_id).first())


# 查询所有用户
def get_all_users(db: Session, page_num: int, page_size: int = 5):
    skip = (page_num - 1) * page_size
    return [get_dict_from_sqlalchemy(obj) for obj in db.query(User).offset(skip).limit(page_size).all()]


# 插入新用户
def create_user(db: Session, user_data: UserCreate):
    db_user = User(
        username=user_data.username,
        password=user_data.password,
        stu_no=user_data.stu_no,
        role=0  # 默认角色为 0，普通用户
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return get_dict_from_sqlalchemy(db_user)
    except IntegrityError:
        db.rollback()
        return None


# 修改用户密码
def update_user_password(db: Session, user_id: str, user_data: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    elif db_user.password == user_data.password:
        return -1 # 原密码错误
    else:
        db_user.password = user_data.password
        db.commit()
        db.refresh(db_user)
        return get_dict_from_sqlalchemy(db_user)


# 删除用户
def delete_user(db: Session, user_id: str):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return get_dict_from_sqlalchemy(db_user)
    return None


# 用户登录
def login_user(db: Session, username: str, password: str):
    db_user_dict = get_user_by_username(db, username)
    if db_user_dict and db_user_dict["password"] == password:
        return db_user_dict
    return None
