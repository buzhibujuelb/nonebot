from nonebot import on_command, CommandSession
import json, os, aiohttp
from nonebot.log import logger
from pyppeteer import launch

__plugin_name__ = "stock"
__plugin_usage__ = "美股/stock + 参数 查看今天川建国是否需要坐火箭\n不带参数/文字/text 查看文本信息\n图片/pic 查看截图\nall 查看两者"

WIDTH=2560
HEIGHT=1440

URL=[
    "https://www.tradingview.com/symbols/SPX/",
    "https://api.worldtradingdata.com/api/v1/stock?symbol=^INX&api_token=UtxjmpMwHl5PcrG5XcQPzM2awG1Rglbz54zhfVgXDdg6ESH7Qig5jcV1xpPJ"
]

PATH2PIC=os.path.join(os.path.abspath('.'),'screenshot.png')

async def get_pic(session):
    browser = await launch({
        'headless': False,
        'args': [ '--hide-scrollbars' ],
        'dumpio': True,  
        })
    page = await browser.newPage()
    await page.setViewport({'width':WIDTH,'height':HEIGHT})
    await page.goto(URL[0])
    await page.screenshot({'path': PATH2PIC})
    await browser.close()
    logger.info(f"New request of stock(pic) finished.")
    await session.send(f"[CQ:image,file={PATH2PIC}]")
    os.remove(PATH2PIC)

async def get_text(session):
    async with aiohttp.ClientSession() as Csession:  # 获取session
        async with Csession.get(URL[1]) as resp:  # 提出请求
            json=await resp.json()
    data=json['data'][0]
    logger.info(f"New request of stock(text) finished.")
    await session.send(f"当前：{data['price']}\n日最高：{data['day_high']}\n日最低：{data['day_low']}\n涨/跌幅：{data['change_pct']}%")

@on_command("美股", aliases=("stock",), only_to_me=False, shell_like=True, privileged=True)
async def _(session: CommandSession):
    argv = session.argv
    if not argv or argv[0] in ['text','文字','all']:
        await get_text(session)
    if argv and argv[0] in ['pic','图片','all']:
        await get_pic(session)

if __name__=='__main__':
    import asyncio 
    loop=asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([get_pic(1)]))
