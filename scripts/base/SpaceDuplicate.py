# -*- coding: utf-8 -*-
try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.BaseApp import KBEngine
import random
from KBEDebug import *
from Space import Space
import d_entities
import d_spaces


class SpaceDuplicate(Space):
    """
    这是一个空间的副本实体
    """

    def __init__(self):
        Space.__init__(self)
