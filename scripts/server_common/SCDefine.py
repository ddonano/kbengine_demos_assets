# -*- coding: utf-8 -*-
import KBEngine
import GlobalConst
from KBEDebug import *

# 服务端timer定义
TIMER_TYPE_BUFF_TICK = 1  # buff的tick
TIMER_TYPE_SPACE_SPAWN_TICK = 2  # space出生怪
TIMER_TYPE_CREATE_SPACES = 3  # 创建space
TIMER_TYPE_DESTROY = 4  # 延时销毁entity
TIMER_TYPE_HEARDBEAT = 5  # 心跳
TIMER_TYPE_FIGTH_WATI_INPUT_TIMEOUT = 6  # 战斗回合等待用户输入超时
TIMER_TYPE_SPAWN = 7  # 出生点出生timer
TIMER_NPC_TYPE_DESTROY = 8  # entity销毁
TIMER_TYPE_SPACE_SPAWN_OMS_TICK = 9  # space出生怪,从oms生成
TIMER_TYPE_CREATE_SPACES_INIT_DELAY = 10  # 延迟初始化创建space
TIMER_TYPE_CREATE_NPC_DELAY = 11  # 延迟创建NPC
TIMER_TYPE_DEL_NPC_DELAY = 12  # 延迟销毁NPC
TIMER_TYPE_DEL_SPACE_DELAY = 13  # 延迟销毁分区