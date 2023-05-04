# -*- coding: utf-8 -*-
import KBEngine

import GlobalConst
import SqlUtil
from KBEDebug import *
from interfaces.GameObject import GameObject

import d_spaces


class Space(KBEngine.Entity, GameObject):
    """
    游戏场景，在这里代表野外大地图
    """

    def __init__(self):
        KBEngine.Entity.__init__(self)
        GameObject.__init__(self)

        # 一个space代表的是一个抽象的空间，这里向这个抽象的空间添加了几何资源数据，如果数据是3D场景的
        # 该space中使用navigate寻路使用的是3D的API，如果是2D的几何数据navigate使用的是astar寻路
        resPath = KBEngine.globalData["spaceSqlInit"].get(self.spaceUType)['resPath']
        # KBEngine.addSpaceGeometryMapping(self.spaceID, None, resPath, True, {0 : "srv_xinshoucun_1.navmesh", 1 : "srv_xinshoucun.navmesh"})
        KBEngine.addSpaceGeometryMapping(self.spaceID, None, resPath)

        DEBUG_MSG('created space[%d] spaceID:[%d] entityID = %i, res = %s.' % (
        self.spaceUType, self.spaceID, self.id, resPath))

        KBEngine.globalData["space_%i" % self.spaceID] = self.base
        sql = SqlUtil.getConcatSql(GlobalConst.SQL_UPDATE_SPACES_STATUS, str(self.spaceUType))
        KBEngine.executeRawDatabaseCommand(sql, self.onSqlCallback)

    def onSqlCallback(self, result, rows, insertid, error):
        DEBUG_MSG(
            'onSqlCallback:sql=%s, result=%s, rows=%s, insertid=%s, error=%s' % (GlobalConst.SQL_UPDATE_SPACES_STATUS,
                                                                                 str(result), str(rows),
                                                                                 str(insertid), str(error)))

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------
    def onDestroy(self):
        """
        KBEngine method.
        """
        self.destroySpace()
        del KBEngine.globalData["space_%i" % self.spaceID]


    def onEnter(self, entityCall):
        """
        defined method.
        进入场景
        """
        DEBUG_MSG('Space::onEnter space[%d] entityID = %i.' % (self.spaceUType, entityCall.id))

    def onLeave(self, entityID):
        """
        defined method.
        离开场景
        """
        DEBUG_MSG('Space::onLeave space[%d] entityID = %i.' % (self.spaceUType, entityID))

    def destroyBy(self, entityID):
        DEBUG_MSG('Space::destroyBy space[%d] entityID = %i.' % (self.spaceUType, entityID))
        KBEngine.entities[entityID].destroy()
