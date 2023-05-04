# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

'''
操作redis工具类(暂时不可使用)
'''


class RedisUtil:
    pass


singleton = RedisUtil()


def __string_encode(src):
    if(isinstance(src, str)):
        return src.replace(' ', '%20').replace(';', '%3b')
    return src


def set(key, value):
    redis_key = key
    val = __string_encode(value)
    cmd = f'SET {redis_key} {val};'
    KBEngine.executeRawDatabaseCommand(cmd, redisCallback, -1, 'redis')


def delete(key):
    redis_key = key
    cmd = f'DEL {redis_key};'
    KBEngine.executeRawDatabaseCommand(cmd, redisCallback, -1, 'redis')


def setEx(key, value, ex):
    redis_key = key
    val = __string_encode(value)
    cmd = f'SETEX {redis_key} {ex} {val};'
    KBEngine.executeRawDatabaseCommand(cmd, redisCallback, -1, 'redis')


def setExWithCallback(key, value, ex, callback):
    redis_key = key
    val = __string_encode(value)
    cmd = f'SETEX {redis_key} {ex} {val};'
    KBEngine.executeRawDatabaseCommand(cmd, callback, -1, 'redis')


def get(key, callback):
    redis_key = key
    cmd = f'GET {redis_key};'
    KBEngine.executeRawDatabaseCommand(cmd, callback, -1, 'redis')


def h_set(key, field, value):
    redis_key = key
    redis_field = field
    val = __string_encode(value)
    cmd = f'HSET {redis_key} {redis_field} {val};'
    KBEngine.executeRawDatabaseCommand(cmd, redisCallback, -1, 'redis')


def h_get(key, field, callback):
    redis_key = key
    redis_field = field
    cmd = f'HGET {redis_key} {redis_field};'
    KBEngine.executeRawDatabaseCommand(cmd, callback, -1, 'redis')


def r_pop(key, callback):
    """
    Redis RPOP 用于移除并返回列表 key 的最后一个元素
    """
    redis_key = key
    cmd = f'RPOP {redis_key};'
    KBEngine.executeRawDatabaseCommand(cmd, callback, -1, 'redis')


def l_push(key, value):
    """
    redis LPUSH 用于将一个值插入到列表key的头部
    """
    redis_key = key
    val = __string_encode(value)
    cmd = f'LPUSH {redis_key} {val};'
    KBEngine.executeRawDatabaseCommand(cmd, redisCallback, -1, 'redis')


def redisCallback(result, rows, insertid, error):
    DEBUG_MSG('onSqlCallback: result=%s, rows=%s, insertid=%s, error=%s' % (
        str(result), str(rows), str(insertid), str(error)))
    pass


def redisReturn(result, rows, insertid, error):
    DEBUG_MSG('onSqlCallback: result=%s, rows=%s, insertid=%s, error=%s' % (
        str(result), str(rows), str(insertid), str(error)))
    return result
