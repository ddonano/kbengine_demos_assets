# -*- coding: utf-8 -*-
import KBEngine
import random
import time
from KBEDebug import *


class Hall(KBEngine.Entity):
    def __init__(self):
        DEBUG_MSG("Hall load end")
        KBEngine.Entity.__init__(self)
        KBEngine.globalData["Halls"] = self
        self.players = []

    def updatePlayer(self, player):
        if player is None:
            DEBUG_MSG("UpdatePlayer player None")
            return
        DEBUG_MSG("UpdatePlayer:%i", player.id)
        if player in self.players:
            self.players.remove(player)
        DEBUG_MSG("UpdatePlayer nums: %i" % len(self.players))

    def addPlayer(self, player):
        DEBUG_MSG("reqAddPlayer: %i" % player.id)
        if player in self.players:
            return
        self.players.append(player)

    def reqPlayerSum(self, player):
        player.OnPlayerSum(len(self.players))
