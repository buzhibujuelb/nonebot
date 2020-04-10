import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission as perm

__plugin_name__ = "help"
__plugin_usage__ = "@不休不眠 help/usage/帮助\n或 help/usage/帮助  [插件名]"


@on_command("usage", aliases=("help", "帮助"))
async def _(session: CommandSession):
    plugins = list(filter(lambda p: p.name, nonebot.get_loaded_plugins()))

    arg = session.current_arg_text.strip().lower()
    if not arg:
        await session.send("这里是不知不觉的 bot 不休不眠，现在支持的功能有：\n" + "\n".join(p.name for p in plugins) + "\n输入 help [功能名] 查询具体用法")
        return

    flag = 0
    for p in plugins:
        if p.name.lower() == arg:
            flag = 1
            await session.send(p.usage)
    if flag == 0:
        await session.send("未能识别插件名")
