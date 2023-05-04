# -*- coding: utf-8 -*-
import GlobalConst
import Space
import SqlUtil

try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
import Functor
from KBEDebug import *
import d_entities
import d_spaces
import copy

CONST_WAIT_CREATE = -1


class SpaceAlloc:
    """
    普通的场景分配器
    """

    def __init__(self, utype):
        self._spaces = {}
        # 从数据库读取 最大分区容量
        self._spacesEntityMaxNum = KBEngine.globalData["spaceSqlInit"][utype].get('partitionSize', 50)
        self._spacesEntityList = {}
        self._spacesEntityNum = {}
        # npc 列表 按照分区分组成  结构：{spaceKey1:[uid1,uid2],spaceKey2:[uid1,uid2]}
        self._spacesNpcList = {}
        self._utype = utype
        self._tempKeys = []
        #  定时回收 剩余空的space 个数，超过此值会被回收
        self._leftEmptyMaxSpaceNum = 2
        self._pendingLogonEntities = {}
        self._pendingEnterEntityMBs = {}

    def init(self):
        spaceKey = self.createSpace(0, {})
        return spaceKey

    def getSpaces(self):
        return self._spaces

    def clearSpacesEntityNum(self, spaceKey, entityId):
        entity_list = self._spacesEntityList.get(spaceKey)
        DEBUG_MSG("SpaceAlloc::clearSpacesEntityNum,entityId:%i, spaceKey:%s,entity_list = %s" % (
            entityId, spaceKey, entity_list))
        if entity_list is not None and entityId in entity_list:
            entity_list.remove(entityId)
            DEBUG_MSG("SpaceAlloc::clearSpacesEntityNum remove,entityId:%i, spaceKey:%s,_spacesEntityList=%s" % (
                entityId, spaceKey, entity_list))

    def setSpacesEntityMaxNum(self):
        self._spacesEntityMaxNum = KBEngine.globalData["spaceSqlInit"][self._utype].get('partitionSize', 50)

    def createSpace(self, spaceKey, context):
        """
        """
        if spaceKey <= 0:
            spaceKey = KBEngine.genUUID64()

        context = copy.copy(context)
        spaceData = KBEngine.globalData["spaceSqlInit"].get(self._utype)
        KBEngine.createEntityAnywhere(spaceData["entityType"],
                                      {"spaceUType": self._utype, "spaceKey": spaceKey, "context": context, },
                                      Functor.Functor(self.onSpaceCreatedCB, spaceKey))
        return spaceKey

    def onSpaceCreatedCB(self, spaceKey, space):
        """
        一个space创建好后的回调
        """
        DEBUG_MSG(
            "Spaces::onSpaceCreatedCB: spaceType=%i,spaceKey=%s, entityID=%i" % (self._utype, spaceKey, space.id))

    def onSpaceLoseCell(self, spaceKey):
        """
        space的cell创建好了
        """
        del self._spaces[spaceKey]
        del self._spacesEntityList[spaceKey]
        if self._spacesNpcList.get(spaceKey):
            del self._spacesNpcList[spaceKey]

    def onNpcCreateSuccess(self, uid, spaceKey):
        if self._spacesNpcList.get(spaceKey) is None:
            self._spacesNpcList[spaceKey] = []
        self._spacesNpcList[spaceKey].append(uid)
        all_create = True
        if len(self._spacesNpcList.keys()) < len(self._spaces.keys()):
            DEBUG_MSG("Spaces::onNpcCreateSuccess: uid:%i not create in all space:%i" % (uid, self._utype))
        else:
            for uid_list in self._spacesNpcList.values():
                if uid not in uid_list:
                    all_create = False
        if all_create:
            Space.updateNpcSqlStatus(uid)
            updateKey = f'npcSqlUpdate_{self._utype}'
            updateData = {}
            updateData = KBEngine.globalData.get(updateKey)
            if uid in updateData.keys():
                del updateData[uid]
            KBEngine.globalData[updateKey] = updateData
            DEBUG_MSG("Spaces::onNpcCreateSuccess: uid:%i onNpcCreateSuccess in all space:%i" % (uid, self._utype))

    def onNpcDelSuccess(self, uid, spaceKey):
        if self._spacesNpcList.get(spaceKey) is None:
            self._spacesNpcList[spaceKey] = []
        if uid in self._spacesNpcList.get(spaceKey):
            self._spacesNpcList[spaceKey].remove(uid)
        all_del = True
        if len(self._spacesNpcList.keys()) < len(self._spaces.keys()):
            DEBUG_MSG("Spaces::onNpcDelSuccess: uid:%i not del in all space:%i" % (uid, self._utype))
        else:
            for uid_list in self._spacesNpcList.values():
                if uid in uid_list:
                    all_del = False
        if all_del:
            Space.updateNpcSqlStatus(uid)
            # 删除时，如果存在npcSqlInit_全局变量里，则这里也要删除
            initKey = f'npcSqlInit_{self._utype}'
            initData = {}
            initData = KBEngine.globalData.get(initKey)
            if initData and uid in initData.keys():
                del initData[uid]
                KBEngine.globalData[initKey] = initData
            DEBUG_MSG("Spaces::onNpcDelSuccess: uid:%i in all space:%i" % (uid, self._utype))

    def onSpaceGetCell(self, spaceEntityCall, spaceKey):
        """
        space的cell创建好了
        """
        DEBUG_MSG(
            "Spaces::onSpaceGetCell: space %i. entityID=%i, spaceKey=%i" % (self._utype, spaceEntityCall.id, spaceKey))
        self._spaces[spaceKey] = spaceEntityCall
        self._spacesEntityList[spaceKey] = []
        pendingLogonEntities = self._pendingLogonEntities.pop(spaceKey, [])
        pendingEnterEntityMBs = self._pendingEnterEntityMBs.pop(spaceKey, [])

        for e, context in pendingLogonEntities:
            self.loginToSpace(e, context)
        for mb, pos, dir, context in pendingEnterEntityMBs:
            self.teleportSpace(mb, pos, dir, context)

    def alloc(self, context, entityId):
        """
        virtual method.
        分配一个space
        """
        if self._spaces == {}:
            return None
        spaceKey = context.get("spaceKey", 0)
        if spaceKey == 0:
            for spaceKey, entityList in self._spacesEntityList.items():
                # 如果进入房间用户数小于最大值 或者本身就在房间里，则可无需新建房间进入
                if len(entityList) < self._spacesEntityMaxNum or entityId in entityList:
                    return [spaceKey, self._spaces[spaceKey]]
        elif self._spaces.get(spaceKey):
            return [spaceKey, self._spaces[spaceKey]]
        return [self.init(), CONST_WAIT_CREATE]

    def destroySpace(self):
        count = 0
        self._tempKeys = list(self._spaces.keys())
        DEBUG_MSG("SpaceAlloc::destroySpace,before spaceNum:%i" % (len(self._tempKeys)))
        for spaceKey in self._tempKeys:
            entityList = self._spacesEntityList.get(spaceKey)
            DEBUG_MSG("SpaceAlloc::destroySpace,spaceKey:%s,entity_list = %s" % (spaceKey, entityList))
            if len(entityList) == 0:
                count = count + 1
                if count > self._leftEmptyMaxSpaceNum:
                    self._spaces[spaceKey].destroySelf()
        DEBUG_MSG("SpaceAlloc::destroySpace,Now spaceNum:%i" % (len(list(self._spaces.keys()))))

    def loginToSpace(self, avatarEntity, context):
        """
        virtual method.
        某个玩家请求登陆到某个space中
        """
        spaceKey = context.get("spaceKey", 0)
        space = self.alloc({"spaceKey": spaceKey}, avatarEntity.id)  # space 是一个list:[spaceKey,space]
        if space is None:
            ERROR_MSG("Spaces::loginToSpace: not found space %i. login to space is failed! spaces=%s" % (
                self._utype, str(self._spaces)))
            return
        if space[1] == CONST_WAIT_CREATE:
            if space[0] not in self._pendingLogonEntities:
                self._pendingLogonEntities[space[0]] = [(avatarEntity, context)]
            else:
                self._pendingLogonEntities[space[0]].append((avatarEntity, context))
            DEBUG_MSG("Spaces::loginToSpace: avatarEntity=%s add pending." % avatarEntity.id)
            return
        self._spacesEntityList[space[0]].append(avatarEntity.id)
        DEBUG_MSG("Spaces::loginToSpace: entityCall=%s,%s,_spacesEntityList=%s " % (
            avatarEntity, self._utype, self._spacesEntityList[space[0]]))
        space[1].loginToSpace(avatarEntity, context)

    def teleportSpace(self, entityCall, position, direction, context):
        """
        virtual method.
        请求进入某个space中
        """
        space = self.alloc(context, entityCall.id)
        if space is None:
            ERROR_MSG("Spaces::teleportSpace: not found space %i. login to space is failed!" % self._utype)
            return

        if space[1] == CONST_WAIT_CREATE:
            if space[0] not in self._pendingEnterEntityMBs:
                self._pendingEnterEntityMBs[space[0]] = [(entityCall, position, direction, context)]
            else:
                self._pendingEnterEntityMBs[space[0]].append((entityCall, position, direction, context))

            DEBUG_MSG("Spaces::teleportSpace: entityId=%s add pending." % (entityCall.id))
            return
        self._spacesEntityList[space[0]].append(entityCall.id)
        DEBUG_MSG("Spaces::teleportSpace: entityId=%s,spaceUType=%s,_spacesEntityList=%s " % (
            entityCall.id, self._utype, self._spacesEntityList[space[0]]))
        space[1].teleportSpace(entityCall, position, direction, context)


class SpaceAllocDuplicate(SpaceAlloc):
    """
    副本分配器
    """

    def __init__(self, utype):
        SpaceAlloc.__init__(self, utype)

    def init(self):
        """
        virtual method.
        """
        pass  # 副本不需要初始化创建一个

    def alloc(self, context, entityId):
        """
        virtual method.
        分配一个space
        对于副本来说创建副本则将玩家的dbid作为space的key，
        任何一个人想进入到这个副本需要知道这个key。
        """
        spaceKey = context.get("spaceKey", 0)
        space = self._spaces.get(spaceKey)

        assert spaceKey != 0

        if space is None:
            self.createSpace(spaceKey, context)
            return CONST_WAIT_CREATE

        return space
