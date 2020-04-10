from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm
import random as rd
import cn2an

__plugin_name__ = "mute"
__plugin_usage__ = "自动禁言刷同样消息第三遍及其以后的人"

group_list = []
lst = {}
tot = {}


@on_natural_language(keywords={}, only_to_me=False, permission=perm.GROUP_MEMBER)
async def _(session: NLPSession):
    msg = session.msg.strip()
    global tot, lst
    userid = session.event["user_id"]

    groupid = session.event["group_id"]

    if not groupid in group_list:
        return

    #    print("userid=",userid)
    #    print("groupid=",groupid)

    if groupid in lst and lst[groupid] == msg:
        tot[groupid] += 1
    else:
        tot[groupid] = 1

    lst[groupid] = msg

    if tot[groupid] >= 3:
        bot = session.bot
        await session.send(cn2an.an2cn(tot[groupid]) + "连击！")
        await bot.set_group_ban(group_id=groupid, user_id=userid, duration=30*(2**tot[groupid]))
