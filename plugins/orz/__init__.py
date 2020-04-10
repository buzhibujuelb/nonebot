__plugin_name__ = "orz"
__plugin_usage__ = r"""自动替换句子中的已存在字典中的人名
若只有人名则随机添加字典中的描述
插入人名/描述 add/ins/append name/desc xxx yyy zzz
删除人名/描述 del/rm/rem name/desc xxx yyy zzz
展示人名/描述 show/list/ls  name/desc
保存/读取配置文件 save/sav load/read xxx"""


from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm
import json, os, re, threading
import random as rd

group_list = []

desc = []
name = []


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


@on_command("save", aliases=("sav",), only_to_me=False)
async def save(session: CommandSession):
    if not session.event["group_id"] in group_list:
        return
    msg = validateTitle(session.current_arg_text.strip())
    try:
        with open(os.path.join(os.path.dirname(__file__), "config", msg + ".json"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"desc": desc, "name": name}, ensure_ascii=0))
    except Exception as e:
        await session.send(str(e))
    else:
        await session.send("文件 %s.json 保存成功" % msg)


@on_command("load", aliases=("read",), only_to_me=False)
async def save(session: CommandSession):
    if not session.event["group_id"] in group_list:
        return
    msg = validateTitle(session.current_arg_text.strip())
    try:
        with open(os.path.join(os.path.dirname(__file__), "config", msg + ".json"), "r", encoding="utf-8") as f:
            d = json.loads(f.read())
            global name, desc
            name = d["name"]
            desc = d["desc"]
    except Exception as e:
        await session.send(str(e))
    else:
        await session.send("文件 %s.json 读取成功" % msg)


@on_natural_language(keywords={}, only_to_me=False, permission=perm.GROUP_MEMBER)
async def _(session: NLPSession):
    msg = session.msg.strip()

    ret = ""

    if not session.event["group_id"] in group_list:
        return

    if name.count(msg):
        await session.send(msg + desc[rd.randint(0, len(desc) - 1)])
        return

    if desc.count(msg):
        await session.send(name[rd.randint(0, len(name) - 1)] + msg)
        return

    rd_name = {}
    r = list(name)
    rd.shuffle(r)

    for i in range(len(name)):
        rd_name[name[i]] = r[i]

    flag = 0
    while True:
        fir = ""
        pos = len(msg) + 1
        for str in name:
            if msg.find(str) != -1:
                if msg.find(str) < pos:
                    pos = msg.find(str)
                    fir = str

        if pos == len(msg) + 1:
            break

        ret = ret + msg[0:pos] + rd_name[fir]
        msg = msg[pos + len(fir) :]
        flag = 1

    ret += msg
    if flag:
        await session.send(ret)


def ins(l, cur):
    if l.count(cur):
        return "重复"
    else:
        l.append(cur)
        return "插入成功"


def rem(l, cur):
    if l.count(cur):
        l.remove(cur)
        return "删除成功"
    else:
        return "未找到"


@on_command("add", aliases=("ins", "append"), only_to_me=False, shell_like=True)
async def add(session: CommandSession):
    if not session.event["group_id"] in group_list:
        return
    msg = session.argv

    if len(msg) < 2:
        await session.send("非法输入")
        return

    typ = msg[0]

    if typ == "name":
        for cur in msg[1:]:
            await session.send(ins(name, cur))
    elif typ == "desc":
        for cur in msg[1:]:
            await session.send(ins(desc, cur))
    else:
        await session.send("非法输入")


@on_command("show", aliases=("list", "ls"), only_to_me=False, shell_like=True)
async def show(session: CommandSession):
    if not session.event["group_id"] in group_list:
        return
    msg = session.argv
    if len(msg) < 1:
        await session.send("非法输入")
        return
    for typ in msg:
        if typ == "name":
            await session.send("name=[%s]" % ",".join(name))
        elif typ == "desc":
            await session.send("desc=[%s]" % ",".join(desc))
        else:
            await session.send("非法输入")


@on_command("del", aliases=("rm", "rem"), only_to_me=False, shell_like=True)
async def Del(session: CommandSession):
    if not session.event["group_id"] in group_list:
        return
    msg = session.argv

    if len(msg) < 2:
        await session.send("非法输入")
        return

    typ = msg[0]

    if typ == "name":
        for cur in msg[1:]:
            await session.send(rem(name, cur))
    elif typ == "desc":
        for cur in msg[1:]:
            await session.send(rem(desc, cur))
    else:
        await session.send("非法输入")

