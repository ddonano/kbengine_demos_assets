# -*- coding: utf-8 -*-
import random

import Utils

try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
import GlobalConst
import d_spaces
import d_avatar_inittab
from KBEDebug import *


class Teleport:
    def __init__(self):
        # 如果登录是一个副本, 无论如何登录都放置在主场景上
        # 因为副本是需要钥匙开启的，所有的副本都使用实体SpaceDuplicate创建
        # 因此我们只需要简单判断当前spaceUType所对应的配置中场景的脚本类型是否包含"Duplicate"
        # 就能得出是否在一个副本中
        spacedatas = KBEngine.globalData["spaceSqlInit"][self.cellData["spaceUType"]]
        avatar_inittab = d_avatar_inittab.datas[self.roleType]

        if "Duplicate" in spacedatas["entityType"]:
            self.cellData["spaceUType"] = avatar_inittab["spaceUType"]
            self.cellData["direction"] = (0, 0, avatar_inittab["spawnYaw"])
            self.cellData["position"] = avatar_inittab["spawnPos"]

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------
    def onClientEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        if self.cell is not None:
            return

        # 防止使用同一个号登陆不同的demo造成无法找到匹配的地图从而无法加载资源导致无法进入游戏
        # 这里检查一下， 发现不对则强制同步到匹配的地图
        # 忽略机器人的检查
        if hasattr(self, "cellData") and self.getClientType() != 6:
            # 如果角色跳转到了同属某个demo的其他场景那么不强制回到出生的主场景
            loginData = str(self.getClientDatas()[0], 'utf-8')
            loginList = loginData.split("|", 1)
            spaceCode = loginList[0]
            location = ()
            if len(loginList) > 1:
                location = tuple(map(float, loginList[1].split(',')))
            if self.cellData["spaceUType"] in KBEngine.globalData["spaceCodeMapInit"].values():
                spaceUType = KBEngine.globalData["spaceCodeMapInit"].get(bytes(spaceCode, encoding='utf-8'), 1)

                if self.cellData["spaceUType"] != spaceUType:
                    spacedatas = KBEngine.globalData["spaceSqlInit"][spaceUType]
                    self.spaceUTypeB = spaceUType
                    self.cellData["spaceUType"] = spaceUType
                    spawnPos = spacedatas.get("spawnPos", (0, 0, 0))
                    # 修改 x z 轴坐标，随机*3
                    pos = location if location else Utils.getRandomPos(spawnPos, 3)
                    self.cellData["position"] = pos
                else:
                    if location:
                        self.cellData["position"] = location
                DEBUG_MSG("onClientEnabled id:%i,realPos:%s" % (self.id, self.cellData["position"]))
        KBEngine.globalData["Spaces"].loginToSpace(self, self.spaceUTypeB, {})
