# coding:utf-8
from nonebot import on_command, CommandSession
from nonebot.log import logger
import json, time, html, collections, re, aiohttp, datetime
from urllib import parse
from lxml import html as lhtml
from fake_useragent import UserAgent

if __name__ == "__main__":
    from config import *
else:
    from .config import *

__plugin_name__ = "check"
__plugin_usage__ = "查询各大 oj 最近 %d 条提交记录\ncheck/抓假颓 [oj名] [用户名]\n(可以使用 all 作为第一个参数)\n(目前支持的 oj %s )" % (SUBMISSION_LIMIT, "，".join(URLS))


async def getres(oj, id):
    url = URLS[oj] + id

    if oj in ["uoj", "bzoj"]:
        async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}) as session:
            async with session.get(url) as resp:
                html = await resp.text()
        tree = lhtml.fromstring(html)
        return tree.xpath(PATTERN[oj])
    elif oj in ["luogu", "loj"]:
        async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}, cookies=cookies.setdefault(oj, ""),) as session:
            async with session.get(url) as resp:
                text = await resp.text()
        s = re.findall(PATTERN[oj], text)[0]
        if oj == "luogu":
            s = parse.unquote(s)
            s = s.encode("utf-8").decode("unicode_escape")
            s = s.replace("\\", "")

        s = json.loads(s)
        if oj == "luogu" and s["code"] == 404:
            return
        return s
    elif oj in ["cf", "atcoder"]:
        async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}) as session:
            async with session.get(url) as resp:
                js = await resp.json()

        if oj == "cf" and js["status"] != "OK":
            return
        return js


async def crawl(oj, id, session):

    logger.info(f"Qrying {id} in {oj}")
    oj = oj.lower()
    if not oj in URLS:
        await session.send("暂不支持此 oj")
        return

    res = await getres(oj, id)

    if not res:
        await session.send(f"没有找到 {id} 在 {oj} 的提交记录QAQ")
        return

    ret = f"{id} 在 {oj} 的最近提交记录有："

    # 提交id    题目名  分数    语言    时间
    if oj == "uoj":
        for index in range(0, min(len(res), 6 * SUBMISSION_LIMIT), 6):
            ret = "%s\n%s %s %s %s %s" % (ret, res[index], res[index + 1], res[index + 3], res[index + 4], res[index + 5],)
    elif oj == "loj":
        for _ in range(SUBMISSION_LIMIT):
            cur = res[_]
            ret = f'{ret}\n#{cur["info"]["submissionId"]} #{cur["info"]["problemId"]}.{cur["info"]["problemName"]} {cur["result"]["score"]} {cur["info"]["language"]} {cur["info"]["submitTime"]}'
    elif oj == "bzoj":
        for index in range(0, min(len(res), 11 * SUBMISSION_LIMIT), 11):
            ret = "%s\n#%s #%s %s %s %s" % (ret, res[index], res[index + 2], res[index + 3], res[index + 8], res[index + 10],)
    elif oj == "luogu":
        res = res["currentData"]["records"]["result"]
        for _ in range(SUBMISSION_LIMIT):
            cur = res[_]
            ret = f'{ret}\n#{cur["id"]} #{cur["problem"]["pid"]}.{cur["problem"]["title"]} {cur.setdefault("score",luogu_sta_dict[cur["status"]])} {luogu_lan_dict[cur["language"]]} {(datetime.datetime.utcfromtimestamp(cur["submitTime"])+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}'
    elif oj == "cf":
        res = res["result"]
        for _ in range(SUBMISSION_LIMIT):
            cur = res[_]
            ret = f'{ret}\n#{cur["id"]} #{cur["problem"]["contestId"]}{cur["problem"]["index"]}.{cur["problem"]["name"]} {cur["verdict"]} {cur["programmingLanguage"]} {(datetime.datetime.utcfromtimestamp(cur["creationTimeSeconds"])).strftime("%Y-%m-%d %H:%M:%S")}'
    elif oj == "atcoder":
        res.sort(key=lambda x: x["id"], reverse=True)
        for _ in range(SUBMISSION_LIMIT):
            cur = res[_]
            ret = f'{ret}\n#{cur["id"]} #{cur["contest_id"]}{ATCODER_PROBLEM_NAME[cur["problem_id"]]} {cur["result"]} {cur["language"]} {(datetime.datetime.utcfromtimestamp(cur["epoch_second"])).strftime("%Y-%m-%d %H:%M:%S")}'

    await session.send(ret)


@on_command("check", aliases=("抓假颓",), only_to_me=False, shell_like=True, privileged=True)
async def check(session: CommandSession):
    argv = session.argv
    if len(argv) != 2:
        await session.send("非法输入")
        return

    oj, id = argv[0], html.unescape(argv[1])

    if argv[0] == "all":
        for oj in URLS:
            await crawl(oj, id, session)
    else:
        await crawl(oj, id, session)


if __name__ == "__main__":
    import asyncio

    class temp(object):
        async def send(self, msg):
            with open("crawler.txt", "w", encoding="utf-8") as f:
                f.write(msg)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([crawl("atcoder", html.unescape("buzhibujue"), temp())]))
