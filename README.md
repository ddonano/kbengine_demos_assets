 这是一个KBEngine服务端demos资产库
========

## 主要更新点
1. 使用pycharm 格式化代码
2. 修改excel方式初始化空间和npc，通过数据库配置表创建，这样方便跟后台管理程序联通。  
主要修改了以下文件：
- interface/kbemain.py 增加定时任务，空间的新增，npc的新增和删除通过定时任务驱动
- base/kbemain.py      base入口，修改了空间和NPC的初始化方式和更新方式
3. 修改SpaceAlloc支持space逻辑自动分区，当房间人数超过一定人数时，自动分配至不同的spaceId的空间，
每一个小时定时任务自动回收房间人数为0的空间  
主要修改了以下文件：
- base/SpaceAlloc.py 修改alloc方法，支持动态创建空间
- base/Spaces.py    定时任务，动态回收空间

## 开始

请将kbengine_demos_assets整个文件夹放置于服务端引擎根目录中，通常是这样:

![demo_configure](http://kbengine.github.io/assets/img/screenshots/demo_copy_kbengine.jpg)


## 启动服务端

使用固定参数来启动：(参数的意义:http://www.kbengine.org/cn/docs/startup_shutdown.html)
	
	首先进入对应的资产库kbengine/kbengine_demos_assets目录中，然后在命令行执行如下命令：

	Linux:
		start_server.sh

	Windows:
		start_server.bat


## 关闭服务端

快速杀死服务端进程:

	首先进入对应的资产库kbengine/kbengine_demos_assets目录中，然后在命令行执行如下命令： 

	Linux:
		kill_server.sh

	Windows:
		kill_server.bat


	(注意：如果是正式运营环境，应该使用安全的关闭方式，这种方式能够确保数据安全的存档，安全的告诉用户下线等等)

	Linux:
		safe_kill.sh

	Windows:
		safe_kill.bat


## 直接从代码定义实体（不需要def文件）

https://github.com/kbengine/kbengine_demos_assets/tree/py_entity_def