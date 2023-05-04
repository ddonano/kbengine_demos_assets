在kbengine_demos_assets基础上扩展了一些功能
========

## 主要更新
1. 使用pycharm 格式化代码
2. 修改excel方式初始化空间和npc，通过数据库配置表创建，这样方便跟后台管理程序联通。  
主要修改了以下文件：
- sql/init.sql 请在数据库表执行init.sql,创建空间和npc配置表，这种方式破快了kbengine原本的无需创建表的初衷，有其他更好的方式，也欢迎讨论。
- scripts/interface/kbemain.py 增加定时任务，空间的新增，npc的新增和删除通过定时任务驱动
- scripts/base/kbemain.py      base入口，修改了空间和NPC的初始化方式和更新方式
3. 修改SpaceAlloc支持space逻辑自动分区，当房间人数超过一定人数时，自动分配至不同的spaceId的空间，
每一个小时定时任务自动回收房间人数为0的空间  
主要修改了以下文件：
- scripts/base/SpaceAlloc.py 修改alloc方法，支持动态创建空间
- scripts/base/Spaces.py    定时任务，动态回收空间
