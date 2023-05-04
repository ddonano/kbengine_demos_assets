# -*- coding: utf-8 -*-
try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
from KBEDebug import *


def countPlayers():
    """
    KBEngine.addWatcher("players", "UINT32", countPlayers)
    上面代码将这个函数添加到监视器中，可以从GUIConsole等工具中实时监视到函数返回值
    """
    i = 0
    for e in KBEngine.entities.values():
        if e.__class__.__name__ == "Avatar":
            i += 1

    return i


def setup():
    KBEngine.addWatcher("players", "UINT32", countPlayers)
