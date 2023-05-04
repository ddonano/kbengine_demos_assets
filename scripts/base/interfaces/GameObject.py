# -*- coding: utf-8 -*-
try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
from KBEDebug import *


class GameObject:
    """
    服务端游戏对象的基础接口类
    """

    def __init__(self):
        pass

    def getScriptName(self):
        return self.__class__.__name__

    def destroySelf(self):
        """
        virtual method
        """
        if self.cell is not None:
            # 销毁cell实体
            self.destroyCellEntity()
            return

        # 销毁base
        self.destroy()

    def getSpaces(self):
        """
        获取场景管理器
        """
        return KBEngine.globalData["Spaces"]

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------
    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        # DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        if self.isDestroyed:
            self.delTimer(tid)
            return

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG("%s::onGetCell: %i" % (self.getScriptName(), self.id))
        pass

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        DEBUG_MSG("%s::onLoseCell: %i" % (self.getScriptName(), self.id))
        self.destroySelf()

    def onRestore(self):
        """
        KBEngine method.
        entity的cell部分实体被恢复成功
        """
        DEBUG_MSG("%s::onRestore: %s" % (self.getScriptName(), self.cell))
