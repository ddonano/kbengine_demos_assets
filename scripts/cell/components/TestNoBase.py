# -*- coding: utf-8 -*-
try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.CellApp import KBEngine
from KBEDebug import *


class TestNoBase(KBEngine.EntityComponent):
    def __init__(self):
        KBEngine.EntityComponent.__init__(self)

    def onAttached(self, owner):
        """
        """
        INFO_MSG("TestNoBase::onAttached(): owner=%i" % (owner.id))
        self.owner.client.component3.helloCB(888)

    def onDetached(self, owner):
        """
        """
        INFO_MSG("TestNoBase::onDetached(): owner=%i" % (owner.id))

    def hello(self, x, iii):
        print("+++++++++++++++++++++++TestNoBase hello", x, iii)
