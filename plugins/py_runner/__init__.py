# 执行Python代码的输出长度限制
OUTPUT_LENGTH_LIMIT = 1000
# 执行Python代码的时间限制(ms)
EXECUTE_TIME_LIMIT = 2000
EXECUTE_TIME_INTERVAL = 100
# 负责执行的Docker镜像名
DOCKER_IMAGE = "python"

__plugin_name__ = "py_runner"
__plugin_usage__ = "python/py/py3 [命令]\n输出长度限制：%d\npython docker 镜像名：%s\n时间限制：%dms" % (OUTPUT_LENGTH_LIMIT, DOCKER_IMAGE, EXECUTE_TIME_LIMIT)

import ctypes, inspect, os, re, tempfile, time, docker, nonebot, html
from . import util
from threading import Thread
from nonebot.log import logger
from nonebot import on_command, CommandSession
from nonebot import permission as perm

def execute_daemon_calc(container,callback):
    container.start()
    container.reload()
    while container.status == "running":
        container.reload()
        time.sleep(0.1)
    output = container.logs().decode("UTF-8")
    if not output:
        output="无输出！"
    container.remove()
    if len(output) > OUTPUT_LENGTH_LIMIT:
        output = output[:OUTPUT_LENGTH_LIMIT] + "[超出长度限制部分已截断]"
    callback(output)
    logger.info("Output=" + output)


def keeper_thread(thread, container, code,callback):
    all_time = 0
    while all_time < EXECUTE_TIME_LIMIT:
        time.sleep(EXECUTE_TIME_INTERVAL / 1000)
        try:
            container.reload()
        except Exception as ex:
            logger.info(ex)
            return
        if container.status != "running":
            return
        all_time += EXECUTE_TIME_INTERVAL
    logger.info("Waiting timed out , status = {}".format(container.status))
    if container.status == "running":
        util.stop_thread(thread)
        try:
            container.kill()
            container.remove()
        except Exception:
            pass
        output = "代码 '" + code + "' 运行超时."
        logger.info("Killing")
        callback(output)

def run_py(code,callback):
    logger.info("Running .. '{}'".format(code))
    client = docker.from_env()
    tmp_dir = tempfile.mkdtemp()
    file_name = "temp.py"
    with open(os.path.join(tmp_dir, file_name), "w", encoding="utf-8") as file:
        file.write("{}".format(code))
    logger.info("Container created.")
    container = client.containers.create(DOCKER_IMAGE, "python /temp/{}".format(file_name), tty=True, detach=False, volumes={tmp_dir: {"bind": "/temp", "mode": "ro"}}, mem_limit="50m", memswap_limit="50m", oom_kill_disable=True, nano_cpus=int(0.1 * 1 / 1e-9),)

    thd = Thread(target=execute_daemon_calc, args=(container,callback))
    thd.setDaemon(True)
    thd.start()
    keeper = Thread(target=keeper_thread, args=(thd, container, code,callback))
    keeper.setDaemon(True)
    keeper.start()
    keeper.join()
    thd.join()

@on_command("python", aliases=("py","py3"), only_to_me=False)
async def run_python_in_docker(session: CommandSession):
    def callback(msg):
        bot=session.bot
        event=session.event.copy()
        event['message']=msg
        bot.sync.send_msg(**event)
    
    new=Thread(target=run_py, args=(html.unescape(session.current_arg),callback))
    new.start()
