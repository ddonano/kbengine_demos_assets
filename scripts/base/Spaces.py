# -*- coding: utf-8 -*-

try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
import Functor
import d_spaces
import SCDefine
import Watcher
from KBEDebug import *
from SpaceAlloc import *
from interfaces.GameObject import GameObject


class Spaces(KBEngine.Entity, GameObject):
    """
    这是一个脚本层封装的空间管理器
    KBEngine的space是一个抽象空间的概念，一个空间可以被脚本层视为游戏场景、游戏房间、甚至是一个宇宙。
    """

    def __init__(self):
        KBEngine.Entity.__init__(self)
        GameObject.__init__(self)
        self._npc = {}
        self._temSpaces = []
        # 初始化空间分配器
        self.initAlloc()

        # 向全局共享数据中注册这个管理器的entityCall以便在所有逻辑进程中可以方便的访问
        KBEngine.globalData["Spaces"] = self

    def initAlloc(self):
        # 注册一个定时器，在这个定时器中我们每个周期都创建出一些NPC，直到创建完所有
        self._spaceAllocs = {}
        # 延迟初始化，为了初始化时从数据库异步加载空间数据
        self.addTimer(1, 0, SCDefine.TIMER_TYPE_CREATE_SPACES_INIT_DELAY)
        self.addTimer(3600, 3600, SCDefine.TIMER_TYPE_DEL_SPACE_DELAY)

    def initDelay(self, tid):
        self.addTimer(3, 1, SCDefine.TIMER_TYPE_CREATE_SPACES)
        self._tmpDatas = list(KBEngine.globalData["spaceSqlInit"].keys())
        if -1 in self._tmpDatas:
            self._tmpDatas.remove(-1)
        for utype in self._tmpDatas:
            DEBUG_MSG("%s::initAlloc:spaceType:%i" % (self.getScriptName(), utype))
            spaceData = KBEngine.globalData["spaceSqlInit"].get(utype)
            if spaceData["entityType"] == "SpaceDuplicate":
                self._spaceAllocs[utype] = SpaceAllocDuplicate(utype)
            else:
                self._spaceAllocs[utype] = SpaceAlloc(utype)

    def spaceDelay(self, tid):
        self._temSpaces = list(self._spaceAllocs.keys())
        for spaceType in self._temSpaces:
            DEBUG_MSG("%s::spaceDelay:spaceType:%i" % (self.getScriptName(), spaceType))
            if self._spaceAllocs[spaceType]:
                self._spaceAllocs[spaceType].destroySpace()

    def getSpaceAllocs(self):
        return self._spaceAllocs

    def createSpaceOnTimer(self, tid):
        """
        创建space
        """
        if len(self._tmpDatas) > 0:
            spaceUType = self._tmpDatas.pop(0)
            self._spaceAllocs[spaceUType].init()

        if len(self._tmpDatas) <= 0:
            self.delTimer(tid)

    def updateSpaceOnTimer(self, update):
        for key in update:
            self._tmpDatas.append(key)
        for utype in self._tmpDatas:
            DEBUG_MSG("%s::initAlloc:spaceType:%i" % (self.getScriptName(), utype))
            #  如果已经存在，则只需要更新最大分区容量，更新全局变量
            if self._spaceAllocs.get(utype):
                self._spaceAllocs[utype].setSpacesEntityMaxNum()
                sql = SqlUtil.getConcatSql(GlobalConst.SQL_UPDATE_SPACES_STATUS,
                                           str(utype))
                KBEngine.executeRawDatabaseCommand(sql, self.onSqlCallback)
            else:
                spaceData = KBEngine.globalData["spaceSqlInit"].get(utype)
                if spaceData["entityType"] == "SpaceDuplicate":
                    self._spaceAllocs[utype] = SpaceAllocDuplicate(utype)
                else:
                    self._spaceAllocs[utype] = SpaceAlloc(utype)
                    self.addTimer(3, 10, SCDefine.TIMER_TYPE_CREATE_SPACES)

    def onSqlCallback(self, result, rows, insertid, error):
        DEBUG_MSG(
            'onSqlCallback:sql=%s, result=%s, rows=%s, insertid=%s, error=%s' % (GlobalConst.SQL_UPDATE_SPACES_STATUS,
                                                                                 str(result), str(rows),
                                                                                 str(insertid), str(error)))

    def loginToSpace(self, avatarEntity, spaceUType, context):
        """
        defined method.
        某个玩家请求登陆到某个space中
        """
        self._spaceAllocs[spaceUType].loginToSpace(avatarEntity, context)

    def logoutSpace(self, avatarID, spaceKey):
        """
        defined method.
        某个玩家请求登出这个space
        """
        DEBUG_MSG("%s::logoutSpace: %i, spaceKey:%s" % (self.getScriptName(), avatarID, spaceKey))
        for spaceAlloc in self._spaceAllocs.values():
            space = spaceAlloc.getSpaces().get(spaceKey)
            if space:
                space.logoutSpace(avatarID)

    def clearSpacesEntityNum(self, avatarID, spaceKey, spaceUType):
        """
        defined method.
        用户退出，清除统计的用户数据
        """
        DEBUG_MSG("%s::delSpacesEntityNum: %i,spaceUtype:%i, spaceKey:%s" % (
            self.getScriptName(), avatarID, spaceUType, spaceKey))
        self._spaceAllocs[spaceUType].clearSpacesEntityNum(spaceKey, avatarID)

    def teleportSpace(self, entityCall, spaceUType, position, direction, context):
        """
        defined method.
        请求进入某个space中
        """
        DEBUG_MSG(
            "%s::teleportSpace: %i, spaceUType:%s, arg:%s" % (self.getScriptName(), self.id, spaceUType, position))
        self._spaceAllocs[spaceUType].teleportSpace(entityCall, position, direction, context)

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------
    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        # DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        if SCDefine.TIMER_TYPE_CREATE_SPACES == userArg:
            self.createSpaceOnTimer(tid)
        elif SCDefine.TIMER_TYPE_CREATE_SPACES_INIT_DELAY == userArg:
            self.initDelay(tid)
        elif SCDefine.TIMER_TYPE_DEL_SPACE_DELAY == userArg:
            self.spaceDelay(tid)
        GameObject.onTimer(self, tid, userArg)

    def onSpaceLoseCell(self, spaceUType, spaceKey):
        """
        defined method.
        space的cell创建好了
        """
        self._spaceAllocs[spaceUType].onSpaceLoseCell(spaceKey)

    def onSpaceGetCell(self, spaceUType, spaceEntityCall, spaceKey):
        """
        defined method.
        space的cell创建好了
        """
        self._spaceAllocs[spaceUType].onSpaceGetCell(spaceEntityCall, spaceKey)

    def updateEntityFromOms(self, spaceUType):
        INFO_MSG("%s,updateEntityFromOms:%i" % (self.getScriptName(), spaceUType))
        spaces = self._spaceAllocs[spaceUType].getSpaces().values()
        if len(spaces) <= 0:
            ERROR_MSG("space %i not found!" % spaceUType)
            return
        for space in spaces:
            space.updateEntityFromOms()

    def delEntityFromOms(self, spaceUType):
        spaces = self._spaceAllocs[spaceUType].getSpaces().values()
        if len(spaces) <= 0:
            ERROR_MSG("space %i not found!" % spaceUType)
            return
        for space in spaces:
            space.delEntityFromOms()

    def onNpcCreateSuccess(self, uid, spaceKey, spaceUType):
        self._spaceAllocs[spaceUType].onNpcCreateSuccess(uid, spaceKey)

    def onNpcDelSuccess(self, uid, spaceKey, spaceUType):
        self._spaceAllocs[spaceUType].onNpcDelSuccess(uid, spaceKey)
