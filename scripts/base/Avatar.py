# -*- coding: utf-8 -*-
try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
import random
import SCDefine
import time
import GlobalConst
import d_spaces
import d_avatar_inittab
from KBEDebug import *
from interfaces.GameObject import GameObject
from interfaces.Teleport import Teleport


class Avatar(KBEngine.Proxy,
             GameObject,
             Teleport):
    """
    角色实体
    """

    def __init__(self):
        KBEngine.Proxy.__init__(self)
        GameObject.__init__(self)
        Teleport.__init__(self)

        self.accountEntity = None
        self.cellData["dbid"] = self.databaseID
        self.nameB = self.cellData["name"]
        self.spaceUTypeB = self.cellData["spaceUType"]

        self._destroyTimer = 0

    def onClientEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        INFO_MSG("Avatar[%i-%s] entities enable. spaceUTypeB=%s, entityCall:%s" % (
            self.id, self.nameB, self.spaceUTypeB, self.client))
        Teleport.onClientEnabled(self)

        if self._destroyTimer > 0:
            self.delTimer(self._destroyTimer)
            self._destroyTimer = 0

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG('Avatar::onGetCell: %s' % self.cell)

    def createCell(self, space):
        """
        defined method.
        创建cell实体
        """
        self.createCellEntity(space)
        DEBUG_MSG('Avatar::createCell: %s' % self)

    def destroySelf(self):
        """
        """
        if self.client is not None:
            return

        if self.cell is not None:
            # 销毁cell实体
            self.destroyCellEntity()
            return

        # 如果帐号ENTITY存在 则也通知销毁它
        if self.accountEntity != None:
            if time.time() - self.accountEntity.relogin > 1:
                self.accountEntity.destroy()
            else:
                DEBUG_MSG("Avatar[%i].destroySelf: relogin =%i" % (self.id, time.time() - self.accountEntity.relogin))

        # 销毁base
        if not self.isDestroyed:
            self.destroy()
        # spacesEntity = KBEngine.globalData["Spaces"]
        # spaceAlloc = spacesEntity.getSpaceAllocs().get(utype)
    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------
    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        # DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        if SCDefine.TIMER_TYPE_DESTROY == userArg:
            self.onDestroyTimer()

        GameObject.onTimer(self, tid, userArg)

    def onClientDeath(self):
        """
        KBEngine method.
        entity丢失了客户端实体
        """
        DEBUG_MSG("Avatar[%i].onClientDeath:" % self.id)
        # 防止正在请求创建cell的同时客户端断开了， 我们延时一段时间来执行销毁cell直到销毁base
        # 这段时间内客户端短连接登录则会激活entity
        self._destroyTimer = self.addTimer(10, 0, SCDefine.TIMER_TYPE_DESTROY)

    def onClientGetCell(self):
        """
        KBEngine method.
        客户端已经获得了cell部分实体的相关数据
        """
        INFO_MSG("Avatar[%i].onClientGetCell:%s" % (self.id, self.client))
        self.client.component3.helloCB(777)

    def onDestroyTimer(self):
        DEBUG_MSG("Avatar::onDestroyTimer: %i" % (self.id))
        self.destroySelf()

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Avatar::onDestroy: %i." % self.id)

        if self.accountEntity != None:
            self.accountEntity.activeAvatar = None
            self.accountEntity = None

    def updateAvatar(self,name):
        DEBUG_MSG("Avatar::updateAvatar: %i" % (self.id))
        for key, info in self.accountEntity.characters.items():
            info[1] = name
            break
        self.accountEntity.writeToDB()