import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission as perm
from .. import mute, repeater, orz

__plugin_name__ = "switcher"
__plugin_usage__ = "enable/开启 [插件名]\ndisable/关闭 [插件名]\n(只有管理可用，可一次开启/关闭多个\n仅支持：复读[repe]，刷屏禁言[mute]，随机膜人[orz]）"


@on_command("enable", aliases=("开启",), permission=perm.GROUP_ADMIN, shell_like=True, only_to_me=False)
async def enable(session: CommandSession):
    argv = session.argv
    groupid = session.event["group_id"]

    for cur in argv:
        if cur == "orz":
            orz.group_list.append(groupid)
            orz.group_list = list(set(orz.group_list))
            await session.send("已开启本群随机膜人")
        elif cur == "mute":
            mute.group_list.append(groupid)
            mute.group_list = list(set(mute.group_list))
            await session.send("已开启本群刷屏禁言")
        elif cur == "repe":
            repeater.group_list.append(groupid)
            repeater.group_list = list(set(repeater.group_list))
            await session.send("已开启本群刷屏复读")
        else:
            await session.send('未找到功能"' + cur + '"')


@on_command("disable", aliases=("关闭",), permission=perm.GROUP_ADMIN, shell_like=True, only_to_me=False)
async def enable(session: CommandSession):
    argv = session.argv
    groupid = session.event["group_id"]

    for cur in argv:
        if cur == "orz":
            orz.group_list.remove(groupid)
            await session.send("已关闭本群随机膜人")
        elif cur == "mute":
            mute.group_list.remove(groupid)
            await session.send("已关闭本群刷屏禁言")
        elif cur == "repe":
            repeater.group_list.remove(groupid)
            await session.send("已关闭本群刷屏复读")
        else:
            await session.send('未找到功能"' + cur + '"')
