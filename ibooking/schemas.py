from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import time


class Response(BaseModel):
    status: int
    message: str
    data: Optional[dict | list[dict]] = None


class UserBase(BaseModel):
    username: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class UserCreate(UserBase):
    stu_no: str = Field(..., max_length=255)


class UserUpdate(UserBase):
    new_password: str = Field(..., max_length=255)


class StudyroomTimeBase(BaseModel):
    open_time: time
    close_time: time

    @model_validator(mode="before")
    def check_time_range_and_order(cls, values):
        open_time_str = values.get('open_time')
        close_time_str = values.get('close_time')
        open_time = None
        close_time = None

        # 如果存在 open_time 和 close_time，就进行转换和检查
        if open_time_str:
            open_time = time(*map(int, open_time_str.split(":")))
            values['open_time'] = open_time  # 更新为时间类型
            if open_time < time(0, 0) or open_time > time(23, 59):
                raise ValueError("open_time 必须在 00:00 到 23:59 之间")

        if close_time_str:
            close_time = time(*map(int, close_time_str.split(":")))
            values['close_time'] = close_time  # 更新为时间类型
            if close_time < time(0, 0) or close_time > time(23, 59):
                raise ValueError("close_time 必须在 00:00 到 23:59 之间")

        # 检查 close_time 是否大于等于 open_time
        if open_time and close_time and close_time < open_time:
            raise ValueError("close_time 必须大于等于 open_time")

        return values


class StudyroomBase(StudyroomTimeBase):
    room_name: str = Field(..., max_length=255)
    room_row: int = Field(..., ge=1)
    room_column: int = Field(..., ge=1)


class StudyroomCreate(StudyroomBase):
    pass


class StudyroomUpdate(StudyroomBase):
    pass


class SeatBase(BaseModel):
    studyroom_id: str
    seat_name: str
    position_row: int
    position_column: int


class SeatCreate(SeatBase):
    pass


class SeatUpdate(SeatBase):
    pass


class SeatStatusUpdate(SeatBase):
    status: int  # 当前状态，1: 未占用, 2: 已占用, 3: 已签到


class BookingBase(BaseModel):
    user_id: str
    seat_id: str
    begin_time: time
    end_time: time

    @model_validator(mode="before")
    def check_time_range_and_order(cls, values):
        begin_time_str = values.get('begin_time')
        end_time_str = values.get('end_time')
        begin_time = None
        end_time = None

        # 如果存在 begin_time 和 end_time，就进行转换和检查
        if begin_time_str:
            begin_time = time(*map(int, begin_time_str.split(":")))
            values['begin_time'] = begin_time  # 更新为时间类型
            if begin_time < time(0, 0) or begin_time > time(23, 59):
                raise ValueError("begin_time 必须在 00:00 到 23:59 之间")

        if end_time_str:
            end_time = time(*map(int, end_time_str.split(":")))
            values['end_time'] = end_time  # 更新为时间类型
            if end_time < time(0, 0) or end_time > time(23, 59):
                raise ValueError("end_time 必须在 00:00 到 23:59 之间")

        # 检查 end_time 是否大于等于 begin_time
        if begin_time and end_time and end_time < begin_time:
            raise ValueError("end_time 必须大于等于 begin_time")

        return values


class BookingCreate(BookingBase):
    pass
