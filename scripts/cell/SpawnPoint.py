# -*- coding: utf-8 -*-
import json

import KBEngine

import GlobalConst
import SCDefine
import SqlUtil
from KBEDebug import *
from interfaces.GameObject import GameObject
import d_entities
import GlobalDefine


class SpawnPoint(KBEngine.Entity, GameObject):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        self.addTimer(1, 0, SCDefine.TIMER_TYPE_SPAWN)

    def spawnTimer(self):
        spaceType = self.getCurrSpace().spaceUType
        INFO_MSG("SpawnPoint::NPC:spawnTimer:%i,spaceType=%i,spaceId=%i" % (self.spawnEntityNO, spaceType,self.spaceID))
        datas = None
        key = f'npcSqlInit_{spaceType}'
        if key in KBEngine.globalData.keys():
            datas = KBEngine.globalData[key].get(self.spawnEntityNO)
            INFO_MSG("SpawnPoint::NPC:spaceType=%i spaceId=%i,KBEngine.globalData[%s].keys:%s." % (
                spaceType, self.spaceID, key, KBEngine.globalData[key].keys()))
        if datas is None:
            INFO_MSG("SpawnPoint::NPC:spawn:spawnEntityNO=%i not found." % self.spawnEntityNO)
            return

        params = {
            "spawnID": self.id,
            "spawnPos": tuple(self.position),
            "uid": str(datas["id"]),
            "utype": datas["etype"],
            "modelID": datas["modelID"],
            "modelScale": self.modelScale,
            "dialogID": datas["dialogID"],
            "name": datas["name"],
            "state": GlobalDefine.ENTITY_STATE_FREE if datas.get("moveType", 1) else GlobalDefine.ENTITY_STATE_DEAD,
            "descr": datas.get("descr", ''),
        }
        e = KBEngine.createEntity(datas["entityType"], self.spaceID, tuple(self.position), tuple(self.direction),
                                  params)
        # 通知创建成功
        self.getCurrSpaceBase().onNpcCreateSuccess(e.id, datas["id"])

        INFO_MSG(
            "SpawnPoint::createEntity:%s(entityId=%i),spaceID:%s,spaceType=%i,position:%s,direction:%s,params:%s" % (
                datas["entityType"], e.id, self.spaceID, spaceType, list(self.position), list(self.direction), params))


    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------

    def onSqlCallback(self, result, rows, insertid, error):
        DEBUG_MSG('onSqlCallback:sql=%s, result=%s, rows=%s, insertid=%s, error=%s' % ("UPDATE t_npc_config",
                                                                                       str(result), str(rows),
                                                                                       str(insertid), str(error)))

    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        if SCDefine.TIMER_TYPE_SPAWN == userArg:
            self.spawnTimer()

        GameObject.onTimer(self, tid, userArg)

    def onRestore(self):
        """
        KBEngine method.
        entity的cell部分实体被恢复成功
        """
        GameObject.onRestore(self)
        self.addTimer(1, 0, SCDefine.TIMER_TYPE_SPAWN)

    def onDestroy(self):
        """
        KBEngine method.
        当前entity马上将要被引擎销毁
        可以在此做一些销毁前的工作
        """
        DEBUG_MSG("onDestroy(%i)" % self.id)

    def onEntityDestroyed(self, entityNO):
        """
        defined.
        出生的entity销毁了 需要重建?
        """
        self.addTimer(1, 0, SCDefine.TIMER_TYPE_SPAWN)
