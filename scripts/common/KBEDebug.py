# -*- coding: utf-8 -*-
import sys
try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine


def printMsg(args, isPrintPath):
    for m in args: print(m)


def TRACE_MSG(*args):
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_NORMAL)
    printMsg(args, False)


def DEBUG_MSG(*args):
    if KBEngine.publish() == 0:
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_DBG)
        printMsg(args, True)


def INFO_MSG(*args):
    if KBEngine.publish() <= 1:
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)
        printMsg(args, False)


def WARNING_MSG(*args):
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_WAR)
    printMsg(args, True)


def ERROR_MSG(*args):
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_ERR)
    printMsg(args, True)
