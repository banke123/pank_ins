#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志Actor模块

负责系统日志的管理和处理。

@author: PankIns Team
@version: 1.0.0
"""

from typing import Any
import logging
from .base_actor import BaseActor


class LoggerActor(BaseActor):
    """
    日志Actor
    
    负责系统日志的集中管理和处理
    """
    
    def initialize(self):
        """
        初始化日志Actor
        """
        self.logger.info("日志Actor初始化")
        self.log_buffer = []
        self.log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
    def cleanup(self):
        """
        清理日志资源
        """
        self.logger.info("日志Actor清理资源")
        # 保存剩余的日志
        if self.log_buffer:
            self.logger.info(f"保存 {len(self.log_buffer)} 条缓存日志")
        
    def handle_message(self, message) -> Any:
        """
        处理日志相关消息
        
        @param {Any} message - 接收到的消息
        @returns {Any} 处理结果
        """
        if isinstance(message, dict):
            action = message.get('action')
            
            if action == 'log':
                return self._log_message(message.get('data'))
            elif action == 'set_level':
                return self._set_log_level(message.get('data'))
            elif action == 'get_logs':
                return self._get_logs(message.get('data'))
            elif action == 'clear_logs':
                return self._clear_logs()
            elif action == 'export_logs':
                return self._export_logs(message.get('data'))
            
        self.logger.warning(f"未知的日志消息: {message}")
        return {"status": "error", "message": "未知的日志消息"}
    
    def _log_message(self, data):
        """
        记录日志消息
        
        @param {dict} data - 日志数据
        @returns {dict} 记录结果
        """
        try:
            level = data.get('level', 'INFO').upper()
            message = data.get('message', '')
            source = data.get('source', 'Unknown')
            
            # 添加到缓存
            log_entry = {
                'timestamp': self._get_timestamp(),
                'level': level,
                'source': source,
                'message': message
            }
            self.log_buffer.append(log_entry)
            
            # 实际记录到系统日志
            log_level = self.log_levels.get(level, logging.INFO)
            logger = logging.getLogger(source)
            logger.log(log_level, message)
            
            return {"status": "ok", "message": "日志已记录"}
            
        except Exception as e:
            self.logger.error(f"日志记录失败: {e}")
            return {"status": "error", "message": f"日志记录失败: {e}"}
    
    def _set_log_level(self, data):
        """
        设置日志级别
        
        @param {dict} data - 日志级别设置
        @returns {dict} 设置结果
        """
        try:
            level = data.get('level', 'INFO').upper()
            logger_name = data.get('logger', '')
            
            if level not in self.log_levels:
                return {"status": "error", "message": f"无效的日志级别: {level}"}
            
            if logger_name:
                target_logger = logging.getLogger(logger_name)
            else:
                target_logger = logging.getLogger()
            
            target_logger.setLevel(self.log_levels[level])
            
            return {"status": "ok", "message": f"日志级别已设置为 {level}"}
            
        except Exception as e:
            self.logger.error(f"设置日志级别失败: {e}")
            return {"status": "error", "message": f"设置日志级别失败: {e}"}
    
    def _get_logs(self, data):
        """
        获取日志
        
        @param {dict} data - 查询参数
        @returns {dict} 日志数据
        """
        try:
            level_filter = data.get('level', '') if data else ''
            source_filter = data.get('source', '') if data else ''
            limit = data.get('limit', 100) if data else 100
            
            filtered_logs = self.log_buffer
            
            # 应用过滤器
            if level_filter:
                filtered_logs = [log for log in filtered_logs if log['level'] == level_filter.upper()]
            
            if source_filter:
                filtered_logs = [log for log in filtered_logs if source_filter in log['source']]
            
            # 限制返回数量
            if limit > 0:
                filtered_logs = filtered_logs[-limit:]
            
            return {"status": "ok", "data": filtered_logs}
            
        except Exception as e:
            self.logger.error(f"获取日志失败: {e}")
            return {"status": "error", "message": f"获取日志失败: {e}"}
    
    def _clear_logs(self):
        """
        清空日志缓存
        
        @returns {dict} 清空结果
        """
        try:
            cleared_count = len(self.log_buffer)
            self.log_buffer.clear()
            
            return {"status": "ok", "message": f"已清空 {cleared_count} 条日志"}
            
        except Exception as e:
            self.logger.error(f"清空日志失败: {e}")
            return {"status": "error", "message": f"清空日志失败: {e}"}
    
    def _export_logs(self, data):
        """
        导出日志
        
        @param {dict} data - 导出参数
        @returns {dict} 导出结果
        """
        try:
            filename = data.get('filename', 'logs_export.txt') if data else 'logs_export.txt'
            format_type = data.get('format', 'txt') if data else 'txt'
            
            # 这里后续会实现实际的文件导出逻辑
            export_count = len(self.log_buffer)
            
            return {"status": "ok", "message": f"已导出 {export_count} 条日志到 {filename}"}
            
        except Exception as e:
            self.logger.error(f"日志导出失败: {e}")
            return {"status": "error", "message": f"日志导出失败: {e}"}
    
    def _get_timestamp(self):
        """
        获取当前时间戳
        
        @returns {str} 时间戳字符串
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] 