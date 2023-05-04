# -*- coding: utf-8 -*-
import random


def getRandomPos(spawnPos, distance):
    """
    随机坐标
    """
    if isinstance(spawnPos, tuple):
        pos = list(spawnPos)
        if random.random() > 0.5:
            pos[0] = pos[0] + distance * round(random.random(), 3)
        else:
            pos[0] = pos[0] - distance * round(random.random(), 3)
        if random.random() > 0.5:
            pos[2] = pos[2] + distance * round(random.random(), 3)
        else:
            pos[2] = pos[2] - distance * round(random.random(), 3)
        return tuple(pos)
    return spawnPos

