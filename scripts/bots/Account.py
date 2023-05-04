# -*- coding: utf-8 -*-
import random
import uuid

import KBEngine
import copy
from KBEDebug import *


class Account(KBEngine.Entity):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        DEBUG_MSG("Account::__init__:%s." % (self.__dict__))
        self.base.reqAvatarList()

    def onReqAvatarList(self, infos):
        """
        defined method.
        """
        avatarid = random.choice(
            ['Fixed_a1094535139784003584', 'Fixed_a1094533377417170944', 'Fixed_a1094535645960871936',
             'Fixed_a1095897540940926976'])
        DEBUG_MSG("Account:onReqAvatarList::%s" % (list(infos['values'])))
        self.base.reqCreateAvatar(1, "kbe_bot_%s" % self.id, avatarid, str(uuid.uuid4()))
        self.characters = copy.deepcopy(infos["values"])

    def onCreateAvatarResult(self, retcode, info):
        """
        defined method.
        """
        DEBUG_MSG("Account:onCreateAvatarResult::%s, retcode=%i" % (dict(info), retcode))

        if retcode == 0:
            self.base.selectAvatarGame(info["dbid"])
        else:
            if len(self.characters) > 0:
                for infos in self.characters:
                    self.base.selectAvatarGame(infos["dbid"])
                    break

    def onRemoveAvatar(self, dbid):
        """
        defined method.
        """
        DEBUG_MSG("Account:onRemoveAvatar:: dbid=%i" % (dbid))
