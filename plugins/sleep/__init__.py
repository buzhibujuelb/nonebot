from nonebot import on_command, CommandSession
import threading
import time, asyncio
from datetime import datetime 

@on_command("sleep",privileged=True)
async def sleep(session: CommandSession):
    await session.send("BEGIN "+datetime.now().strftime('%m/%d %H:%M:%S'))
    await asyncio.sleep(3)
    await session.send("END "+datetime.now().strftime('%m/%d %H:%M:%S'))
