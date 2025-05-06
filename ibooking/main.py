from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller import user_router, studyroom_router, seat_router, booking_router, notification_router
from database import engine, Base
import uvicorn
from controller.booking_controller import scheduler
from contextlib import asynccontextmanager

# 创建数据库表
Base.metadata.create_all(bind=engine)


# 使用 lifespan 事件管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时的操作
    scheduler.start()
    yield
    # 应用关闭时的操作
    scheduler.shutdown()


# 创建 FastAPI 应用。将 lifespan 事件注册到 FastAPI 应用
app = FastAPI(lifespan=lifespan)

# 配置 CORS
origins = [
    "http://localhost:8080",  # Vue 前端
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有的 HTTP 方法
    allow_headers=["*"],  # 允许所有的 HTTP 头
)

# 引入用户路由
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(studyroom_router, prefix="/studyroom", tags=["StudyRoom"])
app.include_router(seat_router, prefix="/seat", tags=["Seat"])
app.include_router(booking_router, prefix="/booking", tags=["Booking"])
app.include_router(notification_router, prefix="/notification", tags=["Notification"])


# 根路由，查看服务器是否正常启动
@app.get("/")
def read_root():
    return {"message": "Welcome to the study room backend API!"}


if __name__ == '__main__':
    uvicorn.run(app="main:app", host="localhost", port=8090)
