# -*- coding: utf-8 -*-
import json

import GlobalConst
import SqlUtil

try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
import SCDefine
import copy
import math
from KBEDebug import *
from interfaces.GameObject import GameObject
import xml.etree.ElementTree as etree


def onSqlCallback(result, rows, insertid, error):
    DEBUG_MSG('onSqlCallback:sql=%s, result=%s, rows=%s, insertid=%s, error=%s' % ("UPDATE t_npc_config",
                                                                                   str(result), str(rows),
                                                                                   str(insertid), str(error)))


def updateNpcSqlStatus(uid):
    sql = SqlUtil.getConcatSql(GlobalConst.SQL_UPDATE_NPC_STATUS, str(uid))
    KBEngine.executeRawDatabaseCommand(
        sql,
        onSqlCallback)


class Space(KBEngine.Entity, GameObject):
    """
    一个可操控cellapp上真正space的实体
    注意：它是一个实体，并不是真正的space，真正的space存在于cellapp的内存中，通过这个实体与之关联并操控space。
    """

    def __init__(self):
        KBEngine.Entity.__init__(self)
        GameObject.__init__(self)
        self.createCellEntityInNewSpace(None)
        self.tmpDelUid = 0
        self.tmpDelTime = 0
        self.spaceUTypeB = self.cellData["spaceUType"]
        self.spaceResName = KBEngine.globalData["spaceSqlInit"][self.spaceUTypeB]['resPath']
        # 从npcSqlInit_spaceUtype 拷贝数据过来
        #  暂存NPC数据，如果已经创建成功则会删除
        initKey = f'npcSqlInit_{self.spaceUTypeB}'
        self.tmpUpdateNpcDatas = copy.deepcopy(KBEngine.globalData.get(initKey, {}))
        # 地图上存在的npc列表 key：uid ，value= entityId
        self.npc_list = {}
        # 地图上存在的需要删除的npc列表 uid list
        self.del_list = []
        # 这个地图上创建的entity总数
        self.tmpCreateEntityDatas = []
        if self.tmpUpdateNpcDatas:
            for i in self.tmpUpdateNpcDatas.values():
                self.tmpCreateEntityDatas.append([i['id'],
                                                  i['position'],
                                                  i['direction'],
                                                  0,
                                                  ])
        self.avatars = {}

    # self.createSpawnPointDatas()

    def createSpawnPointDatas(self):
        """
        """
        res = r"scripts\data\spawnpoints\%s_spawnpoints.xml" % (self.spaceResName.replace("\\", "/").split("/")[-1])
        if (len(self.spaceResName) == 0 or not KBEngine.hasRes(res)):
            return

        res = KBEngine.getResFullPath(res)

        tree = etree.parse(res)
        root = tree.getroot()

        DEBUG_MSG("Space::createSpawnPointDatas: %s" % (res))

        for child in root:
            positionNode = child[0][0]
            directionNode = child[0][1]
            scaleNode = child[0][2]

            scale = int(((float(scaleNode[0].text) + float(scaleNode[1].text) + float(scaleNode[2].text)) / 3.0) * 10)
            position = (float(positionNode[0].text), float(positionNode[1].text), float(positionNode[2].text))
            direction = [float(directionNode[0].text) / 360 * (math.pi * 2),
                         float(directionNode[1].text) / 360 * (math.pi * 2),
                         float(directionNode[2].text) / 360 * (math.pi * 2)]

            if direction[0] - math.pi > 0.0:
                direction[0] -= math.pi * 2
            if direction[1] - math.pi > 0.0:
                direction[1] -= math.pi * 2
            if direction[2] - math.pi > 0.0:
                direction[2] -= math.pi * 2

            self.tmpCreateEntityDatas.append([int(child.attrib['name']), \
                                              position, \
                                              direction, \
                                              scale, \
                                              ])

    def spawnOnTimer(self, tid):
        INFO_MSG(
            "spawnOnTimer begin:spaceUType= %i,spaceKey=%s,space entityId=%i" % (
                self.spaceUTypeB, self.spaceKey, self.id))
        """
        出生怪物
        """
        if len(self.tmpCreateEntityDatas) <= 0:
            self.delTimer(tid)
            return

        datas = self.tmpCreateEntityDatas.pop(0)
        INFO_MSG("spawnOnTimer: spawn uid=%i !" % datas[0])
        if datas is None:
            ERROR_MSG("Space::onTimer: spawn %i is error!" % datas[0])

        KBEngine.createEntityAnywhere("SpawnPoint",
                                      {"spawnEntityNO": datas[0],
                                       "position": datas[1],
                                       "direction": (0, 0, datas[2]),
                                       "modelScale": datas[3],
                                       "createToCell": self.cell})

    def loginToSpace(self, avatarEntityCall, context):
        """
        defined method.
        某个玩家请求登陆到这个space中
        """
        DEBUG_MSG("Space::loginToSpace: entityId=%s,spaceUType=%s,spaceKey=%s " % (
            avatarEntityCall.id, self.spaceUTypeB, self.spaceKey))
        avatarEntityCall.createCell(self.cell)
        self.onEnter(avatarEntityCall)

    def logoutSpace(self, entityID):
        """
        defined method.
        某个玩家请求登出这个space
        """
        self.onLeave(entityID)

    def destroySelf(self):
        if self.cell is not None:
            # 销毁cell实体
            self.destroyCellEntity()
            return
        # 销毁base
        if not self.isDestroyed:
            self.destroy()

    def teleportSpace(self, entityCall, position, direction, context):
        """
        defined method.
        请求进入某个space中
        """
        DEBUG_MSG("Space::teleportSpace: entityId=%s,spaceUType=%s,spaceKey=%s " % (
            entityCall.id, self.spaceUTypeB, self.spaceKey))
        entityCall.cell.onTeleportSpaceCB(self.cell, self.spaceUTypeB, position, direction)

    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        # DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        if SCDefine.TIMER_TYPE_SPACE_SPAWN_TICK == userArg:
            self.spawnOnTimer(tid)
        elif SCDefine.TIMER_TYPE_SPACE_SPAWN_OMS_TICK == userArg:
            self.spawnOnTimer(tid)
        elif SCDefine.TIMER_NPC_TYPE_DESTROY == userArg:
            self.delEntityOnTimer(tid)
        elif SCDefine.TIMER_TYPE_CREATE_NPC_DELAY == userArg:
            self.delayCreateNpc(tid)
        elif SCDefine.TIMER_TYPE_DEL_NPC_DELAY == userArg:
            self.delayDelNpc(tid)
        GameObject.onTimer(self, tid, userArg)

    def onEnter(self, entityCall):
        """
        defined method.
        进入场景
        """
        self.avatars[entityCall.id] = entityCall

        if self.cell is not None:
            self.cell.onEnter(entityCall)

    def onLeave(self, entityID):
        """
        defined method.
        离开场景
        """
        if entityID in self.avatars:
            del self.avatars[entityID]

        if self.cell is not None:
            self.cell.onLeave(entityID)
        # 用户退出，则从记录的space的用户列表里清除
        KBEngine.globalData["Spaces"].clearSpacesEntityNum(entityID, self.spaceKey, self.spaceUTypeB)

    def destroyBy(self, entityID):
        """
        defined method.
        离开场景
        """
        if entityID in self.avatars:
            del self.avatars[entityID]

        if self.cell is not None:
            self.cell.destroyBy(entityID)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        KBEngine.globalData["Spaces"].onSpaceLoseCell(self.spaceUTypeB, self.spaceKey)
        GameObject.onLoseCell(self)

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG("Space::onGetCell: %i" % self.id)
        self.addTimer(1, 1, SCDefine.TIMER_TYPE_SPACE_SPAWN_TICK)
        DEBUG_MSG("Space::space entityId=%i,create NPC list: %s" % (self.id, self.tmpCreateEntityDatas))
        KBEngine.globalData["Spaces"].onSpaceGetCell(self.spaceUTypeB, self, self.spaceKey)
        GameObject.onGetCell(self)

    def updateEntityFromOms(self):
        self.addTimer(1, 0, SCDefine.TIMER_TYPE_CREATE_NPC_DELAY)

    def onNpcDelSuccess(self, uid):
        if self.npc_list and self.npc_list.get(uid):
            del self.npc_list[uid]
        KBEngine.globalData["Spaces"].onNpcDelSuccess(uid, self.spaceKey, self.spaceUTypeB)

    def onNpcCreateSuccess(self, entityId, uid):
        if self.tmpUpdateNpcDatas.get(uid):
            del self.tmpUpdateNpcDatas[uid]
        self.npc_list.update({uid: entityId})
        KBEngine.globalData["Spaces"].onNpcCreateSuccess(uid, self.spaceKey, self.spaceUTypeB)

    def delEntityFromOms(self):
        self.addTimer(1, 0, SCDefine.TIMER_TYPE_DEL_NPC_DELAY)

    def delEntityOnTimer(self, tid):

        if len(self.del_list) <= 0:
            self.delTimer(tid)
            return
        uid = self.del_list.pop(0)
        key = f'npcSqlDel_{self.spaceUTypeB}'
        entityID = None
        if self.npc_list is not None:
            entityID = self.npc_list.get(uid)

        if self.tmpDelUid != uid:
            self.tmpDelUid = uid
            self.tmpDelTime = 0
        else:
            self.tmpDelTime += 1
        if entityID is not None:
            self.destroyBy(entityID)
            self.tmpDelTime += 5
        else:
            INFO_MSG("delEntityOnTimer:entityId not found,uid=%i,tmpDelTime=%i" % (uid, self.tmpDelTime))
            if self.tmpDelTime < 3:
                self.del_list.insert(0, uid)
        # 超过三次删除不了，则直接清除掉，不再处理
        if self.tmpDelTime >= 3:
            KBEngine.globalData[key] = copy.copy(self.del_list)
            self.onNpcDelSuccess(uid)

    def delayCreateNpc(self, tid):
        """
        从oms 创建NPC
        """
        # 从npcSqlUpdate_spaceUtype 拷贝数据过来
        typeKey = f'npcSqlUpdate_{self.spaceUTypeB}'
        #  暂存NPC数据，如果已经创建成功则会删除
        npc_update = {}
        npc_del = False
        npc_update = KBEngine.globalData.get(typeKey)
        if npc_update:
            for uid in list(npc_update.keys()):
                # 如果已经创建成功，则删除全局数据，并更新表
                if self.npc_list.get(uid):
                    del npc_update[uid]
                    npc_del = True
                    updateNpcSqlStatus(uid)
        # 如果存在已经更新过的情况，则更新全局数据
        if npc_del:
            KBEngine.globalData[typeKey] = npc_update
        self.tmpUpdateNpcDatas.update(npc_update)
        if self.tmpUpdateNpcDatas is None:
            self.tmpUpdateNpcDatas = {}
        if self.tmpUpdateNpcDatas:
            for i in self.tmpUpdateNpcDatas.values():
                self.tmpCreateEntityDatas.append([i['id'],
                                                  i['position'],
                                                  i['direction'],
                                                  0,
                                                  ])
        DEBUG_MSG(
            "Space::updateEntityFromOms:space entityId=%i,sapceUType=%i,spaceKey=%s, create NPC list: %s" % (
                self.id, self.spaceUTypeB, self.spaceKey, self.tmpCreateEntityDatas))
        self.addTimer(1, 1, SCDefine.TIMER_TYPE_SPACE_SPAWN_OMS_TICK)

    def delayDelNpc(self, tid):

        """
        从oms 删除NPC
        """
        key = f'npcSqlDel_{self.spaceUTypeB}'
        self.del_list = copy.deepcopy(KBEngine.globalData.get(key, []))
        DEBUG_MSG(
            "Space::delEntityFromOms:space entityId=%i,sapceUType=%i,spaceKey=%s, del NPC list: %s" % (
                self.id, self.spaceUTypeB, self.spaceKey, self.del_list))
        self.addTimer(1, 1, SCDefine.TIMER_NPC_TYPE_DESTROY)
