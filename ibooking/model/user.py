from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    username = Column(String(255), nullable=True, unique=True)
    password = Column(String(255), nullable=True)
    stu_no = Column(String(255), nullable=True, unique=True)
    role = Column(Integer, nullable=True) # 用户 0，管理 1
