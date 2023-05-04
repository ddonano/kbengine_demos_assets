# -*- coding: utf-8 -*-
import os
import random

import GlobalConst

try:
    import KBEngine
except ImportError:
    # 这里这样做就是为了编码方便
    # 实际代码运行的时候是不会走到这里的
    # 如果没有请安装pip install kbengine_tips
    from kbengine_tips.Interface import KBEngine
from KBEDebug import *
from Poller import Poller
# import AsyncRequest
import MinHTTPServer
import pickle

"""
interfaces进程主要处理KBEngine服务端与第三方平台的接入接出工作。
(注意：由于interfaces是一个单线程服务器，如果需要使用python的http服务器库，建议使用异步的（例如：Tornado），否则会卡主线程造成阻塞。对外http请求可以使用KBEngine.urlopen异步请求。)
目前支持几种功能:
1: 注册账号
	当客户端请求注册账号后，请求会由loginapp转发到dbmgr，如果dbmgr挂接了interfaces，则dbmgr将请求转发至这里（KBEngine.onRequestCreateAccount）
	此时脚本收到这个请求之后可以使用各种方式与第三方平台通信，可以使用python的http库也能直接使用socket，当与第三方平台交互完毕之后应该将
	交互的结果返回给引擎baseapp层，通过KBEngine.createAccountResponse能够将信息推送到baseapp层。
	
2：账号登陆
	当客户端请求登陆账号后，请求会由loginapp转发到dbmgr，如果dbmgr挂接了interfaces，则dbmgr将请求转发至这里（KBEngine.onRequestAccountLogin）
	此时脚本收到这个请求之后可以使用各种方式与第三方平台通信，可以使用python的http库也能直接使用socket，当与第三方平台交互完毕之后应该将
	交互的结果返回给引擎baseapp层层，通过KBEngine.accountLoginResponse能够将信息推送到baseapp层。
	
3：充值计费
	当baseapp上请求计费entity.charge()后，请求会由loginapp转发到dbmgr，如果dbmgr挂接了interfaces，则dbmgr将请求转发至这里（KBEngine.onRequestCharge）
	此时脚本收到这个请求之后可以使用各种方式与第三方平台通信，可以使用python的http库也能直接使用socket，当与第三方平台交互完毕之后应该将
	交互的结果返回给引擎baseapp层，通过KBEngine.chargeResponse能够将信息推送到baseapp层entity.charge时给入的回调或者回调到onLoseChargeCB接口。
	
	某些平台要求客户端直接与平台请求计费，平台采用回调服务器的方式来完成请求， 参考“平台回调”。
	
4: 平台回调
	要完成此功能应该在脚本层创建一个socket，
	并将socket挂接到KBEngine中（这样可防止阻塞导致主线程卡），然后监听指定的端口。
	使用KBE的KBEngine.registerReadFileDescriptor()和KBEngine.registerWriteFileDescriptor()，具体查看API文档与Poller.py。
"""


# g_poller = Poller()


def onInterfaceAppReady():
    """
    KBEngine method.
    interfaces已经准备好了
    """
    INFO_MSG('onInterfaceAppReady: bootstrapGroupIndex=%s, bootstrapGlobalIndex=%s' % \
             (os.getenv("KBE_BOOTIDX_GROUP"), os.getenv("KBE_BOOTIDX_GLOBAL")))

    # 定时任务，用于定时刷新后台数据 启动成功5分钟以后才定时从后台刷新数据
    KBEngine.addTimer(300, 120, onTick)

    # g_poller.start("localhost", 30040)
    server = MinHTTPServer.MinHTTPServer()
    server.listen(8080)
    # 添加接口 请添加路径 和对应的handler处理方法
    server.route('/index.html', indexHandler)
    server.route('/test', indexHandler)
    server.route('/cmd', indexHandler)


def indexHandler(req, resp):
    resp.body = ('Hello %s' % (req.params.get('name', 'kbengine'))).encode()
    resp.end()
    KBEngine.chargeResponse(req.url, resp.body, KBEngine.SERVER_SUCCESS)
    INFO_MSG('indexHandler: chargeResponse=%s' % resp.body)


def onTick(timerID):
    """
    """
    INFO_MSG('onTick()')

    #  查询新增的房间
    KBEngine.executeRawDatabaseCommand(
        GlobalConst.SQL_QUERY_CREATE_SPACES,
        onSqlCreateSpaceCallback)

    #  查询新增的NPC
    KBEngine.executeRawDatabaseCommand(
        GlobalConst.SQL_QUERY_UPDATE_NPC,
        onSqlCreateNpcCallback)

    #  查询删除的NPC
    KBEngine.executeRawDatabaseCommand(
        GlobalConst.SQL_QUERY_DEL_NPC,
        onSqlDelNpcCallback)


def onInterfaceAppShutDown():
    """
    KBEngine method.
    这个interfaces被关闭前的回调函数
    """
    INFO_MSG('onInterfaceAppShutDown()')
    # g_poller.stop()


def onRequestCreateAccount(registerName, password, datas):
    """
    KBEngine method.
    请求创建账号回调
    @param registerName: 客户端请求时所提交的名称
    @type  registerName: string

    @param password: 密码
    @type  password: string

    @param datas: 客户端请求时所附带的数据，可将数据转发第三方平台
    @type  datas: bytes
    """
    INFO_MSG('onRequestCreateAccount: registerName=%s' % (registerName))

    commitName = registerName

    # 默认账号名就是提交时的名
    realAccountName = commitName

    # 此处可通过http等手段将请求提交至第三方平台，平台返回的数据也可放入datas
    # datas将会回调至客户端
    # 如果使用http访问，因为interfaces是单线程的，同步http访问容易卡住主线程，建议使用
    # KBEngine.urlopen("https://www.baidu.com",onHttpCallback)异步访问。也可以结合异步socket的方式与平台交互（参考Poller.py)。

    KBEngine.createAccountResponse(commitName, realAccountName, datas, KBEngine.SERVER_SUCCESS)


def onRequestAccountLogin(loginName, password, datas):
    """
    KBEngine method.
    请求登陆账号回调
    @param loginName: 客户端请求时所提交的名称
    @type  loginName: string

    @param password: 密码
    @type  password: string

    @param datas: 客户端请求时所附带的数据，可将数据转发第三方平台
    @type  datas: bytes
    """
    INFO_MSG('onRequestAccountLogin: registerName=%s' % (loginName))

    commitName = loginName

    # 默认账号名就是提交时的名
    realAccountName = commitName

    # 此处可通过http等手段将请求提交至第三方平台，平台返回的数据也可放入datas
    # datas将会回调至客户端
    # 如果使用http访问，因为interfaces是单线程的，同步http访问容易卡住主线程，建议使用
    # KBEngine.urlopen("https://www.baidu.com",onHttpCallback)异步访问。也可以结合异步socket的方式与平台交互（参考Poller.py)。

    # 如果返回码为KBEngine.SERVER_ERR_LOCAL_PROCESSING则表示验证登陆成功，但dbmgr需要检查账号密码，KBEngine.SERVER_SUCCESS则无需再检查密码
    KBEngine.accountLoginResponse(commitName, realAccountName, datas, KBEngine.SERVER_ERR_LOCAL_PROCESSING)


def onRequestCharge(ordersID, entityDBID, datas):
    """
    KBEngine method.
    请求计费回调
    @param ordersID: 订单的ID
    @type  ordersID: uint64

    @param entityDBID: 提交订单的实体DBID
    @type  entityDBID: uint64

    @param datas: 客户端请求时所附带的数据，可将数据转发第三方平台
    @type  datas: bytes
    """
    INFO_MSG('onRequestCharge: entityDBID=%s, entityDBID=%s' % (ordersID, entityDBID))

    # 此处可通过http等手段将请求提交至第三方平台，平台返回的数据也可放入datas
    # datas将会回调至baseapp的订单回调中，具体参考API手册charge
    # 如果使用http访问，因为interfaces是单线程的，同步http访问容易卡住主线程，建议使用
    # KBEngine.urlopen("https://www.baidu.com",onHttpCallback)异步访问。也可以结合异步socket的方式与平台交互（参考Poller.py)。

    KBEngine.chargeResponse(ordersID, datas, KBEngine.SERVER_SUCCESS)


def onSqlCreateNpcCallback(result, rows, insertid, error):
    DEBUG_MSG('onSqlCreateNpcCallback: result=%s, rows=%s, insertid=%s, error=%s,%s' % (
        result, str(rows), str(insertid), str(error), isinstance(result, list)))
    if result is not None and len(result):
        KBEngine.chargeResponse("onSqlCreateNpcCallback", pickle.dumps(result), KBEngine.SERVER_SUCCESS)


def onSqlDelNpcCallback(result, rows, insertid, error):
    DEBUG_MSG('onSqlDelNpcCallback: result=%s, rows=%s, insertid=%s, error=%s,%s' % (
        result, str(rows), str(insertid), str(error), isinstance(result, list)))
    if result is not None and len(result):
        KBEngine.chargeResponse("onSqlDelNpcCallback", pickle.dumps(result), KBEngine.SERVER_SUCCESS)


def onSqlCreateSpaceCallback(result, rows, insertid, error):
    DEBUG_MSG('onSqlCreateSpaceCallback: result=%s, rows=%s, insertid=%s, error=%s,%s' % (
        result, str(rows), str(insertid), str(error), isinstance(result, list)))
    if result is not None and len(result):
        KBEngine.chargeResponse("onSqlCreateSpaceCallback", pickle.dumps(result), KBEngine.SERVER_SUCCESS)


def onHttpCallback(httpcode, data, headers, success, url):
    DEBUG_MSG('onHttpCallback: httpcode=%i, data=%s, headers=%s, success=%s, url=%s' % (
        httpcode, data, headers, str(success), url))
