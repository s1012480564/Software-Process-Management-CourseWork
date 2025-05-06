from fastapi import Request, APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio
from service.booking_service import user_messages

# 推送通知的路由
notification_router = APIRouter()


@notification_router.get("/{user_id}")
async def sse_push_notifications(user_id: int):
    async def event_generator():
        while True:
            if user_id in user_messages and user_messages[user_id]:
                message = user_messages[user_id].pop()
                yield f"data: {message}\n\n"
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
