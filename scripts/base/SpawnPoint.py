# -*- coding: utf-8 -*-
try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
from KBEDebug import *
from interfaces.GameObject import GameObject


class SpawnPoint(KBEngine.Entity, GameObject):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        GameObject.__init__(self)
        self.createCellEntity(self.createToCell)
