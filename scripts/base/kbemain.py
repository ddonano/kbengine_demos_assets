# -*- coding: utf-8 -*-
import copy
import json

import SqlUtil

try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine

import GlobalConst
import Watcher
import d_spaces
from KBEDebug import *
import RedisUtil
import pickle


def onBaseAppReady(isBootstrap):
    """
    KBEngine method.
    baseapp已经准备好了
    @param isBootstrap: 是否为第一个启动的baseapp
    @type isBootstrap: BOOL
    """
    INFO_MSG('onBaseAppReady: isBootstrap=%s' % isBootstrap)
    # 安装监视器
    Watcher.setup()
    if isBootstrap:
        # 初始化spaceSqlInit全局变量,深度拷贝d_spaces.datas
        KBEngine.globalData["spaceSqlInit"] = copy.deepcopy(d_spaces.datas, {})
        # 初始化2级场馆
        KBEngine.executeRawDatabaseCommand(
            GlobalConst.SQL_QUERY_SPACES,
            onSqlInitSpaceCallback)

        # 创建大厅
        # KBEngine.createEntityLocally("Hall", {})

        # 初始化查询entity
        KBEngine.executeRawDatabaseCommand(
            GlobalConst.SQL_QUERY_ALL_NPC,
            onSqlInitNpcCallback)

        # 创建spacemanager,创建放这里
        KBEngine.createEntityLocally("Spaces", {})
    # RedisUtil.set("test001", "test001")
    # RedisUtil.setEx("test002", "test002", 60)
    # RedisUtil.h_set("test003", "test002", 60)
    # RedisUtil.h_set("test003", "test003", 61)
    # RedisUtil.h_set("test003", "test004", 62)
    # RedisUtil.h_set("test003", "test005", "hello")
    # RedisUtil.l_push("test004", "1")
    # RedisUtil.l_push("test004", "2")
    # RedisUtil.l_push("test004",1)
    # RedisUtil.l_push("test004",3)
    # RedisUtil.get("test001", RedisUtil.redisCallback)
    INFO_MSG('onBaseAppReady: isBootstrap=%s' % isBootstrap)


def onSqlInitNpcCallback(result, rows, insertid, error):
    DEBUG_MSG('onSqlInitNpcCallback: result=%s, rows=%s, insertid=%s, error=%s,%s' % (
        result, str(rows), str(insertid), str(error), isinstance(result, list)))
    groups = {}
    if result is not None and len(result) > 0:
        for i in result:
            item = [int(i[0]),  # id
                    str(i[1], 'utf-8'),  # name
                    int(i[2]),  # runSpeed
                    int(i[3]),  # moveSpeed
                    str(i[4], 'utf-8'),  # entityType
                    int(i[5]),  # dialogID
                    str(i[6], 'utf-8'),  # modelID
                    int(i[7]),  # etype
                    tuple(map(float, str(i[8], 'utf-8').split(','))),
                    # position
                    float(str(i[9], 'utf-8')),
                    # direction
                    int(i[10]),  # spaceUType,
                    int(i[11])  # moveType,
                    ]
            dict_zip = dict(
                zip(['id', 'name', 'runSpeed', 'moveSpeed', 'entityType', 'dialogID', 'modelID', 'etype',
                     'position', 'direction', 'spaceUType', 'moveType'], item))
            groups.setdefault(int(i[10]), {}).update({int(i[0]): dict_zip})
        for key, value in groups.items():
            DEBUG_MSG('onSqlCallback init entity dict: key=%i,value :%s' % \
                      (key, value))
            initKey = f'npcSqlInit_{key}'
            updateKey = f'npcSqlUpdate_{key}'
            KBEngine.globalData[initKey] = copy.deepcopy(value)
            KBEngine.globalData[updateKey] = copy.deepcopy(value)


def onReadyForShutDown():
    """
    KBEngine method.
    进程询问脚本层：我要shutdown了，脚本是否准备好了？
    如果返回True，则进程会进入shutdown的流程，其它值会使得进程在过一段时间后再次询问。
    用户可以在收到消息时进行脚本层的数据清理工作，以让脚本层的工作成果不会因为shutdown而丢失。
    """
    INFO_MSG('onReadyForShutDown()')
    return True


def onBaseAppShutDown(state):
    """
    KBEngine method.
    这个baseapp被关闭前的回调函数
    @param state:  0 : 在断开所有客户端之前
                         1 : 在将所有entity写入数据库之前
                         2 : 所有entity被写入数据库之后
    @type state: int
    """
    INFO_MSG('onBaseAppShutDown: state=%i' % state)


def onReadyForLogin(isBootstrap):
    """
    KBEngine method.
    如果返回值大于等于1.0则初始化全部完成, 否则返回准备的进度值0.0~1.0。
    在此可以确保脚本层全部初始化完成之后才开放登录。
    @param isBootstrap: 是否为第一个启动的baseapp
    @type isBootstrap: BOOL
    """
    if not isBootstrap:
        INFO_MSG('initProgress: completed!')
        return 1.0

    spacesEntity = KBEngine.globalData["Spaces"]
    if len(KBEngine.globalData["spaceSqlInit"]) <= len(d_spaces.datas):
        DEBUG_MSG("spaceSqlInit waiting:%i,%i" % (len(KBEngine.globalData["spaceSqlInit"]), len(d_spaces.datas)))
        # 返回等待
        return 0.0001
    tmpDatas = list(KBEngine.globalData["spaceSqlInit"].keys())
    count = 0
    total = len(tmpDatas) - 1  # 排除-1的情况

    for utype in tmpDatas:
        if utype == -1:
            continue
        spaceAlloc = spacesEntity.getSpaceAllocs().get(utype)
        if spaceAlloc is None:
            # 返回进度等待
            return 0.0002
        if spaceAlloc.__class__.__name__ != "SpaceAllocDuplicate":
            if len(spaceAlloc.getSpaces()) > 0:
                count += 1
        else:
            count += 1

    if count < total:
        v = float(count) / total
        INFO_MSG('initProgress: %f' % v)
        return v

    INFO_MSG('initProgress: completed!')
    return 1.0


def onSqlInitSpaceCallback(result, rows, insertid, error):
    DEBUG_MSG('onSqlInitSpaceCallback: result=%s, rows=%s, insertid=%s, error=%s,%s' % (
        result, str(rows), str(insertid), str(error), isinstance(result, list)))
    groups = {-1: {}}
    # 合并字典
    groups.update(KBEngine.globalData["spaceSqlInit"])
    codes = {}
    codes = GlobalConst.g_demoMaps
    '''
    SQL_QUERY_SPACES = "SELECT t.id,t.`code`,t.`name`,t.location,t.module_id,t.spawn_pos from t_space_config t WHERE t.`status`=0 and t.del_flag=0;"
    '''
    if result is not None and len(result) > 0:
        for i in result:
            DEBUG_MSG('onSqlQuerySpaceCallback: i[1]=%s, int(i[0]=%i' % (
                i[1], int(i[0])))
            codes.update({i[1]: int(i[0])})
            groups.update({int(i[0]): dict(
                zip(['id', 'code', 'name', 'entityType', 'type', 'resPath', 'spawnPos', 'partitionSize'],
                    [int(i[0]),  # id
                     str(i[1], 'utf-8'),
                     # byte 格式 code
                     str(i[2], 'utf-8'),  # name
                     'Space',  # entityType
                     1,  # type
                     'spaces/empty',  # resPath
                     tuple(map(float, str(i[5], 'utf-8').split(','))),  # position
                     int(i[6])  # 分区大小partitionSize
                     ]))})

    KBEngine.globalData["spaceSqlInit"] = groups
    KBEngine.globalData["spaceCodeMapInit"] = codes

    INFO_MSG("globalData[spaceSqlInit]:%s" % json.dumps(KBEngine.globalData["spaceSqlInit"]))


def onAutoLoadEntityCreate(entityType, dbid):
    """
    KBEngine method.
    自动加载的entity创建方法，引擎允许脚本层重新实现实体的创建，如果脚本不实现这个方法
    引擎底层使用createEntityAnywhereFromDBID来创建实体
    """
    INFO_MSG('onAutoLoadEntityCreate: entityType=%s, dbid=%i' % (entityType, dbid))
    KBEngine.createEntityAnywhereFromDBID(entityType, dbid)


def onInit(isReload):
    """
    KBEngine method.
    当引擎启动后初始化完所有的脚本后这个接口被调用
    @param isReload: 是否是被重写加载脚本后触发的
    @type isReload: bool
    """
    INFO_MSG('onInit::isReload:%s' % isReload)


def onFini():
    """
    KBEngine method.
    引擎正式关闭
    """
    INFO_MSG('onFini()')


def onCellAppDeath(addr):
    """
    KBEngine method.
    某个cellapp死亡
    """
    WARNING_MSG('onCellAppDeath: %s' % (str(addr)))


def onGlobalData(key, value):
    """
    KBEngine method.
    globalData有改变
    """
    DEBUG_MSG('onGlobalData: key=%s' % key)


def onGlobalDataDel(key):
    """
    KBEngine method.
    globalData有删除
    """
    DEBUG_MSG('onDelGlobalData: %s' % key)


def onBaseAppData(key, value):
    """
    KBEngine method.
    baseAppData有改变
    """
    DEBUG_MSG('onBaseAppData: %s' % key)


def onBaseAppDataDel(key):
    """
    KBEngine method.
    baseAppData有删除
    """
    DEBUG_MSG('onBaseAppDataDel: %s' % key)


def onLoseChargeCB(ordersID, dbid, success, datas):
    """
    KBEngine method.
    有一个不明订单被处理， 可能是超时导致记录被billing
    清除， 而又收到第三方充值的处理回调
    """
    DEBUG_MSG('onLoseChargeCB: ordersID=%s, dbid=%i, success=%i, ' % \
              (ordersID, dbid, success))
    if ordersID == "onSqlCreateSpaceCallback":
        data = pickle.loads(datas)
        onSqlCreateSpaceCallback(data)
    elif ordersID == "onSqlCreateNpcCallback":
        data = pickle.loads(datas)
        onSqlCreateNpcCallback(data)
    elif ordersID == "onSqlDelNpcCallback":
        data = pickle.loads(datas)
        onSqlDelNpcCallback(data)
        # onSqlDelNpcCallback


def onSqlDelNpcCallback(result):
    """
    从npc配置表扫描entity_status = 0 的数据更新
    """
    groups = {}
    if result is not None and len(result) > 0:
        for i in result:
            groups.setdefault(int(i[1]), []).append(int(i[0]))  # spaceid id

        for key, value in groups.items():
            DEBUG_MSG('onSqlDelNpcCallback list:key=%i,value :%s' % \
                      (key, value))
            keys = f'npcSqlDel_{key}'
            if keys in KBEngine.globalData.keys():
                # 没处理完，则设置为空不处理
                if len(KBEngine.globalData[keys]):
                    KBEngine.globalData[keys] = []
                    return
            KBEngine.globalData[keys] = value
            # INFO_MSG("globalData Key:%s,value:%s" % (keys, json.dumps(KBEngine.globalData[keys])))
            KBEngine.globalData["Spaces"].delEntityFromOms(key)


def onSqlCreateNpcCallback(result):
    """
    从npc配置表扫描entity_status = 0 的数据更新
    """
    groups = {}  # key:spaceUType value:key:id value:{}
    if result is not None and len(result) > 0:
        for i in result:
            item = [int(i[0]),  # id
                    str(i[1], 'utf-8'),  # name
                    int(i[2]),  # runSpeed
                    int(i[3]),  # moveSpeed
                    str(i[4], 'utf-8'),  # entityType
                    int(i[5]),  # dialogID
                    str(i[6], 'utf-8'),  # modelID
                    int(i[7]),  # etype
                    tuple(map(float, str(i[8], 'utf-8').split(','))),
                    # position
                    float(str(i[9], 'utf-8')),
                    # direction
                    int(i[10]),  # spaceUType,
                    int(i[11])  # moveType,
                    ]
            dict_zip = dict(
                zip(['id', 'name', 'runSpeed', 'moveSpeed', 'entityType', 'dialogID', 'modelID', 'etype',
                     'position', 'direction', 'spaceUType', 'moveType'], item))
            groups.setdefault(int(i[10]), {}).update({int(i[0]): dict_zip})
        for key, value in groups.items():
            DEBUG_MSG('onSqlCreateNpcCallback list:key=%i,value :%s' % \
                      (key, value))
            updateKey = f'npcSqlUpdate_{key}'
            initKey = f'npcSqlInit_{key}'
            initData = KBEngine.globalData.get(initKey, {})
            initData.update(value)
            KBEngine.globalData[initKey] = initData
            if updateKey in KBEngine.globalData.keys():
                if len(KBEngine.globalData[updateKey]):
                    DEBUG_MSG('globalData[%s]: not empty:value=%s' % \
                              (updateKey, KBEngine.globalData[updateKey]))
                    KBEngine.globalData["Spaces"].updateEntityFromOms(key)
                    return
                else:
                    KBEngine.globalData[updateKey] = value
                    # INFO_MSG("globalData Key:%s,value:%s" % (keys, json.dumps(KBEngine.globalData[keys])))
                    KBEngine.globalData["Spaces"].updateEntityFromOms(key)
            else:
                KBEngine.globalData[updateKey] = value
                # INFO_MSG("globalData Key:%s,value:%s" % (keys, json.dumps(KBEngine.globalData[keys])))
                KBEngine.globalData["Spaces"].updateEntityFromOms(key)


def onSqlCreateSpaceCallback(result):
    """
    从space配置表扫描create_status = 0 的数据创建房间
    """

    groups = KBEngine.globalData["spaceSqlInit"]
    codes = KBEngine.globalData["spaceCodeMapInit"]
    updateSpaceIds = []
    '''
    SQL_QUERY_SPACES = "SELECT t.id,t.`code`,t.`name`,t.location,t.module_id,t.spawn_pos from t_space_config t WHERE t.`status`=0 and t.del_flag=0;"
    '''
    if result is not None and len(result) > 0:
        for i in result:
            DEBUG_MSG('onSqlCreateSpaceCallback: i[1]=%s, int(i[0])=%i' % (
                i[1], int(i[0])))
            updateSpaceIds.append(int(i[0]))
            codes.update({i[1]: int(i[0])})
            groups.update({int(i[0]): dict(
                zip(['id', 'code', 'name', 'entityType', 'type', 'resPath', 'spawnPos', 'partitionSize'],
                    [int(i[0]),  # id
                     str(i[1], 'utf-8'),
                     # byte 格式 code
                     str(i[2], 'utf-8'),
                     # name
                     'Space',
                     # entityType
                     1,  # type
                     'spaces/empty',  # resPath
                     tuple(map(float, str(i[5], 'utf-8').split(','))),  # position
                     int(i[6]),  # partitionSize
                     ]))})
        # 合并字典
        KBEngine.globalData["spaceSqlInit"] = groups
        KBEngine.globalData["spaceCodeMapInit"] = codes
        INFO_MSG("updateSpaceIds:%s" % updateSpaceIds)
        # 添加 定时任务
        KBEngine.globalData["Spaces"].updateSpaceOnTimer(updateSpaceIds)
