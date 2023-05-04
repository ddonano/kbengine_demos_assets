/*
删除excel初始化方式，额外空间创建表，从该表读取配置，创建空间，方便跟管理后台联通，kbengine 通过interface 定时任务创建空间
*/
CREATE TABLE `t_space_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `code` varchar(128) COLLATE utf8mb4_bin NOT NULL COMMENT '场馆code',
  `type` smallint(6) DEFAULT '0' COMMENT '类型(1=可进入,2=不可进入)',
  `name` varchar(256) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '场馆名称',
  `location` varchar(256) COLLATE utf8mb4_bin DEFAULT '' COMMENT '场馆生成位置，xyz逗号隔开',
  `tip` varchar(256) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '场馆提示',
  `desc` varchar(512) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '场馆描述',
  `pic` varchar(256) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '场馆图片',
  `url` varchar(256) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '场馆跳转地址',
  `status` tinyint(4) DEFAULT '0' COMMENT '状态（0=启用，1=停用）',
  `del_flag` tinyint(4) DEFAULT '0' COMMENT '删除标志（0=存在,2=删除）',
  `create_by` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL,
  `update_by` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL,
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `module_id` varchar(255) COLLATE utf8mb4_bin DEFAULT '0' COMMENT '区分加载不同的场馆模板',
  `spawn_pos` varchar(255) COLLATE utf8mb4_bin DEFAULT '0,0,0' COMMENT '人物进入时的出生坐标,xyz逗号隔开',
  `create_status` tinyint(4) DEFAULT '0' COMMENT '创建状态，0 未更新  1 已更新',
  `space_id` int(11) DEFAULT '0' COMMENT '每次kbe初始化或者创建空间，都会更新此值，保持kbespaceID值一致',
  `partition_size` mediumint(8) unsigned DEFAULT '100' COMMENT '每个分区最大容纳人数',
  `sort` int(11) DEFAULT '0' COMMENT '排列顺序',
  PRIMARY KEY (`id`),
  KEY `IDX_SPACE_CONFIG_CODE` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

/*
删除excel初始化方式，额外NPC创建表，从该表读取配置，创建NPC，方便跟管理后台联通，kbengine 通过interface 定时任务创建和删除NPC
*/
CREATE TABLE `t_entity_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'NPC配置信息表',
  `name` varchar(255) COLLATE utf8mb4_bin NOT NULL COMMENT 'npc名称',
  `run_speed` int(11) DEFAULT '0' COMMENT '跑步速度',
  `move_speed` int(11) DEFAULT '0' COMMENT '位移速度',
  `entity_type` varchar(255) COLLATE utf8mb4_bin NOT NULL DEFAULT 'NPC' COMMENT '实体类型',
  `dialog_id` int(11) DEFAULT '0' COMMENT '对话框ID',
  `model_id` varchar(256) COLLATE utf8mb4_bin DEFAULT '0' COMMENT '模型ID',
  `etype` tinyint(4) DEFAULT '1',
  `position` varchar(255) COLLATE utf8mb4_bin DEFAULT '0,0,0' COMMENT '位置',
  `direction` varchar(255) COLLATE utf8mb4_bin DEFAULT '0' COMMENT '朝向',
  `status` tinyint(4) DEFAULT '0' COMMENT '状态(0=启用,1=停用)',
  `entity_status` tinyint(4) DEFAULT '0' COMMENT '实体状态(0=未创建,1=创建成功)',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `create_by` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '创建人',
  `update_by` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '更新人',
  `move_type` tinyint(4) DEFAULT '0' COMMENT '移动类型(0 固定位置,1 巡航模式)',
  `del_flag` tinyint(4) DEFAULT '0' COMMENT '删除标志（0=存在,2=删除）',
  `dialog_message` varchar(10240) COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'npc 对话内容',
  `space_type` int(11) DEFAULT '0' COMMENT '对应t_space_config表里的ID',
  `remark` varchar(512) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '描述',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

INSERT INTO `t_space_config` (`id`,`code`, `type`, `name`, `location`, `tip`, `desc`, `pic`, `url`, `status`, `del_flag`, `create_by`, `update_by`, `create_time`, `update_time`, `module_id`, `spawn_pos`, `create_status`, `space_id`, `partition_size`, `sort`) VALUES ('1','kbengine_unity3d_demo', '1', '中央广场测试', '0,0,0', NULL, NULL, '/picture/2023/03/22/1d0e48fd-9e57-4925-b4e7-0fc5bed262fa.png', NULL, '1', '2', NULL, 'admin', NULL, '2023-03-22 20:09:07', '0', '0,1,0', '1', '14', '100', '2');

INSERT INTO `t_entity_config` (`name`, `run_speed`, `move_speed`, `entity_type`, `dialog_id`, `model_id`, `etype`, `position`, `direction`, `status`, `entity_status`, `create_time`, `update_time`, `create_by`, `update_by`, `move_type`, `del_flag`, `dialog_message`, `space_type`, `remark`) VALUES ('测试NPC', '0', '0', 'NPC', '0', 'a1106694216173498368', '2', '0,-0.7,3', '60', '0', '1', '2023-04-18 13:39:56', '2023-04-18 13:39:56', 'admin', 'admin', '0', '0', '链接地址1|https://cn.bing.com/;lianjiedizhi2|https://www.baidu.com/', '1', 'NPCA');
INSERT INTO `t_entity_config` (`name`, `run_speed`, `move_speed`, `entity_type`, `dialog_id`, `model_id`, `etype`, `position`, `direction`, `status`, `entity_status`, `create_time`, `update_time`, `create_by`, `update_by`, `move_type`, `del_flag`, `dialog_message`, `space_type`, `remark`) VALUES ('62626', '0', '0', 'NPC', '0', 'a1094535645960871936', '1', '0,-0.7,6', '66', '0', '1', '2023-04-18 13:52:45', '2023-04-18 13:53:09', 'admin', 'admin', '0', '0', '阿萨撒所', '1', '6666');
INSERT INTO `t_entity_config` (`name`, `run_speed`, `move_speed`, `entity_type`, `dialog_id`, `model_id`, `etype`, `position`, `direction`, `status`, `entity_status`, `create_time`, `update_time`, `create_by`, `update_by`, `move_type`, `del_flag`, `dialog_message`, `space_type`, `remark`) VALUES ('NPC啊', '0', '0', 'NPC', '0', 'a1106692226290823168', '2', '0,-0.7,8', '16', '0', '1', '2023-04-25 16:00:52', '2023-04-25 16:19:06', 'admin', 'admin', '0', '0', '66666666666666666', '1', '66666666666666666');




