from nonebot import on_command, CommandSession
import json, random, os

__plugin_name__ = "poem"
__plugin_usage__ = "poem/古诗/古诗文 随机高考古诗文"

@on_command("poem", aliases=("古诗", "古诗文"), only_to_me=False)
async def randompoem(session: CommandSession):
    with open(os.path.join(os.path.dirname(__file__),'poems.json'),'r',encoding='utf-8') as f:
        a=json.load(f)
    curp=random.choice(a['poems'])
    s=curp['title']
    for x in curp['content']:
        s=s+'\n'+'，'.join(x)+'。'
    await session.send(s)
