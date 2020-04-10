from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm

__plugin_name__ = "repeater"
__plugin_usage__ = "自动复读出现两遍及以上的消息（不包括图片）\necho/say/repe [xxx] : 输出 [xxx]"

import random as rd

group_list = []
lst = {}
tot = {}


@on_natural_language(keywords={}, only_to_me=False, permission=perm.GROUP_MEMBER)
async def _(session: NLPSession):
    msg = session.msg.strip()
    global tot, lst
    groupid = session.event["group_id"]

    if not groupid in group_list:
        return

    if groupid in lst and lst[groupid] == msg:
        tot[groupid] += 1
    else:
        tot[groupid] = 1

    lst[groupid] = msg

    if tot[groupid] >= 2:
        return IntentCommand(60.0, "repe", current_arg=msg)


@on_command("repe", aliases=("echo", "say"), only_to_me=False)
async def _(session: CommandSession):
    await session.send(session.current_arg)
