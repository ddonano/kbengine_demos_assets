# -*- coding: utf-8 -*-

"""
"""
import random

GC_OK = 0x000

# 技能相关
GC_SKILL_MP_NOT_ENGOUH = 0x001  # 法力值不足
GC_SKILL_ENTITY_DEAD = 0x002  # Entity已经死亡

# 不同demo所对应的地图
g_demoMaps = {
}

# ------------------------------------------------------------------------------
# sql语句
# ------------------------------------------------------------------------------
# sql变量部分 使用 %s 代替，实际使用时 %（）替换
# SQL_QUERY_ALL_NPC
SQL_QUERY_ALL_NPC = "SELECT t.id,t.name,t.run_speed,t.move_speed,t.entity_type,t.dialog_id,t.model_id,t.etype,t.position,t.direction,t.space_type,t.move_type from t_entity_config t where t.status = 0 and t.del_flag=0;"
# SQL_QUERY_UPDATE_NPC
SQL_QUERY_UPDATE_NPC = "SELECT t.id,t.name,t.run_speed,t.move_speed,t.entity_type,t.dialog_id,t.model_id,t.etype,t.position,t.direction,t.space_type,t.move_type from t_entity_config t where t.entity_status = 0 and t.status = 0 and t.del_flag=0 limit 50;"

SQL_QUERY_DEL_NPC = "SELECT t.id,t.space_type from t_entity_config t where t.entity_status = 0 and t.status = 1 limit 100;"

# SQL_QUERY_SPACES
SQL_QUERY_SPACES = "SELECT t.id,t.`code`,t.`name`,t.location,t.module_id,t.spawn_pos,t.partition_size from t_space_config t WHERE t.`status`=0 and t.del_flag=0;"

# SQL_QUERY_UPDATE_NPC
SQL_QUERY_CREATE_SPACES = "SELECT t.id,t.`code`,t.`name`,t.location,t.module_id,t.spawn_pos,t.partition_size from t_space_config t WHERE t.`status`=0 and t.del_flag=0 and t.create_status = 0 limit 10;"

# SQL_UPDATE_SPACES
SQL_UPDATE_SPACES_STATUS = "UPDATE t_space_config t set t.create_status = 1 WHERE id=%s;"

SQL_UPDATE_NPC_STATUS = "UPDATE t_entity_config t set t.entity_status = 1 where  t.id=%s  and t.entity_status = 0;"


