from os import path
import nonebot, config

if __name__ == "__main__":
    nonebot.init(config)
    nonebot.load_plugins(path.join(path.dirname(__file__), "plugins"), "plugins")
    nonebot.run(use_reloader=False)
