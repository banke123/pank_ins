#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Actor模块

处理AI相关的任务，包括数据分析、命令生成等。
预留LangChain集成接口。

@author: PankIns Team
@version: 1.0.0
"""

import logging
import json
from typing import Dict, Any, List, Optional
from .base_actor import BaseActor


class AIMessage:
    """AI消息类型定义"""
    ANALYZE_DATA = "analyze_data"
    GENERATE_WORKFLOW = "generate_workflow"
    PROCESS_QUERY = "process_query"
    DIAGNOSE_SIGNAL = "diagnose_signal"
    GENERATE_REPORT = "generate_report"


class AIActor(BaseActor):
    """
    AI Actor类
    
    负责处理AI相关的任务，包括数据分析、命令生成、查询处理等
    """
    
    def __init__(self):
        """
        初始化AI Actor
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.ai_status = "online"
        self.current_tasks = {}
        self.knowledge_base = self._init_knowledge_base()
        
        # 预留LangChain相关属性
        self.llm_chain = None
        self.vector_store = None
        self.memory = None
    
    def on_start(self):
        """
        Actor启动时的初始化
        """
        super().on_start()
        self.logger.info("AI Actor启动完成")
        self._init_ai_components()
    
    def _init_knowledge_base(self) -> Dict[str, Any]:
        """
        初始化知识库
        
        @returns {dict} 知识库数据
        """
        return {
            "signal_patterns": {
                "sine_wave": "正弦波信号，通常表示纯净的周期性信号",
                "square_wave": "方波信号，包含丰富的谐波成分",
                "noise": "噪声信号，可能表示干扰或系统问题",
                "pulse": "脉冲信号，常见于数字系统"
            },
            "common_issues": {
                "high_noise": "信号噪声过高，建议检查接地和屏蔽",
                "distortion": "信号失真，可能是放大器饱和或非线性",
                "frequency_drift": "频率漂移，可能是温度或电源不稳定"
            },
            "measurement_tips": {
                "amplitude": "测量幅度时注意选择合适的垂直刻度",
                "frequency": "频率测量建议使用自动测量功能",
                "phase": "相位测量需要双通道同时采集"
            }
        }
    
    def _init_ai_components(self):
        """
        初始化AI组件（预留LangChain集成）
        """
        try:
            # 这里将来集成LangChain组件
            # from langchain.llms import OpenAI
            # from langchain.chains import ConversationChain
            # from langchain.memory import ConversationBufferMemory
            
            # self.llm_chain = ConversationChain(...)
            # self.memory = ConversationBufferMemory(...)
            
            self.logger.info("AI组件初始化完成（当前使用模拟模式）")
            
        except Exception as e:
            self.logger.warning(f"AI组件初始化失败，使用模拟模式: {e}")
            self.ai_status = "limited"
    
    def on_receive(self, message):
        """
        处理接收到的消息
        
        @param {dict} message - 接收到的消息
        """
        try:
            msg_type = message.get("type")
            data = message.get("data", {})
            task_id = message.get("task_id", f"task_{len(self.current_tasks)}")
            
            if msg_type == AIMessage.ANALYZE_DATA:
                self._handle_data_analysis(data, task_id)
            elif msg_type == AIMessage.GENERATE_WORKFLOW:
                self._handle_workflow_generation(data, task_id)
            elif msg_type == AIMessage.PROCESS_QUERY:
                self._handle_query_processing(data, task_id)
            elif msg_type == AIMessage.DIAGNOSE_SIGNAL:
                self._handle_signal_diagnosis(data, task_id)
            elif msg_type == AIMessage.GENERATE_REPORT:
                self._handle_report_generation(data, task_id)
            else:
                self.logger.warning(f"未知的AI消息类型: {msg_type}")
                
        except Exception as e:
            self.logger.error(f"处理AI消息时发生错误: {e}")
    
    def _handle_data_analysis(self, data: Dict[str, Any], task_id: str):
        """
        处理数据分析任务
        
        @param {dict} data - 分析数据
        @param {str} task_id - 任务ID
        """
        self.logger.info(f"开始数据分析任务: {task_id}")
        
        # 模拟数据分析过程
        signal_data = data.get("signal_data", [])
        time_data = data.get("time_data", [])
        
        if not signal_data or not time_data:
            self._send_task_result(task_id, {
                "status": "error",
                "message": "数据不完整，无法进行分析"
            })
            return
        
        # 简单的信号分析
        analysis_result = self._analyze_signal_characteristics(signal_data, time_data)
        
        self._send_task_result(task_id, {
            "status": "completed",
            "analysis": analysis_result,
            "recommendations": self._generate_recommendations(analysis_result)
        })
    
    def _handle_workflow_generation(self, data: Dict[str, Any], task_id: str):
        """
        处理工作流程生成任务
        
        @param {dict} data - 生成参数
        @param {str} task_id - 任务ID
        """
        self.logger.info(f"开始工作流程生成任务: {task_id}")
        
        objective = data.get("objective", "通用测试")
        signal_type = data.get("signal_type", "unknown")
        
        # 生成工作流程
        workflow = self._generate_test_workflow(objective, signal_type)
        
        self._send_task_result(task_id, {
            "status": "completed",
            "workflow": workflow
        })
    
    def _handle_query_processing(self, data: Dict[str, Any], task_id: str):
        """
        处理查询任务
        
        @param {dict} data - 查询数据
        @param {str} task_id - 任务ID
        """
        query = data.get("query", "")
        context = data.get("context", {})
        
        self.logger.info(f"处理查询: {query[:50]}...")
        
        # 模拟AI查询处理
        response = self._process_user_query(query, context)
        
        self._send_task_result(task_id, {
            "status": "completed",
            "response": response
        })
    
    def _handle_signal_diagnosis(self, data: Dict[str, Any], task_id: str):
        """
        处理信号诊断任务
        
        @param {dict} data - 诊断数据
        @param {str} task_id - 任务ID
        """
        self.logger.info(f"开始信号诊断任务: {task_id}")
        
        signal_data = data.get("signal_data", [])
        symptoms = data.get("symptoms", [])
        
        diagnosis = self._diagnose_signal_issues(signal_data, symptoms)
        
        self._send_task_result(task_id, {
            "status": "completed",
            "diagnosis": diagnosis
        })
    
    def _handle_report_generation(self, data: Dict[str, Any], task_id: str):
        """
        处理报告生成任务
        
        @param {dict} data - 报告数据
        @param {str} task_id - 任务ID
        """
        self.logger.info(f"开始报告生成任务: {task_id}")
        
        test_results = data.get("test_results", {})
        template = data.get("template", "standard")
        
        report = self._generate_test_report(test_results, template)
        
        self._send_task_result(task_id, {
            "status": "completed",
            "report": report
        })
    
    def _analyze_signal_characteristics(self, signal_data: List[float], time_data: List[float]) -> Dict[str, Any]:
        """
        分析信号特征
        
        @param {list} signal_data - 信号数据
        @param {list} time_data - 时间数据
        @returns {dict} 分析结果
        """
        import numpy as np
        
        signal_array = np.array(signal_data)
        
        # 基本统计特征
        amplitude_max = np.max(signal_array)
        amplitude_min = np.min(signal_array)
        amplitude_pp = amplitude_max - amplitude_min
        amplitude_rms = np.sqrt(np.mean(signal_array**2))
        
        # 频域分析
        fft_result = np.fft.fft(signal_array)
        frequencies = np.fft.fftfreq(len(signal_array), time_data[1] - time_data[0])
        dominant_freq_idx = np.argmax(np.abs(fft_result[1:len(fft_result)//2])) + 1
        dominant_frequency = abs(frequencies[dominant_freq_idx])
        
        return {
            "amplitude": {
                "max": float(amplitude_max),
                "min": float(amplitude_min),
                "peak_to_peak": float(amplitude_pp),
                "rms": float(amplitude_rms)
            },
            "frequency": {
                "dominant": float(dominant_frequency),
                "spectrum_peak_count": len(np.where(np.abs(fft_result) > np.max(np.abs(fft_result)) * 0.1)[0])
            },
            "signal_type": self._classify_signal_type(signal_array, dominant_frequency)
        }
    
    def _classify_signal_type(self, signal_data: np.ndarray, dominant_freq: float) -> str:
        """
        分类信号类型
        
        @param {ndarray} signal_data - 信号数据
        @param {float} dominant_freq - 主要频率
        @returns {str} 信号类型
        """
        # 简单的信号分类逻辑
        std_dev = np.std(signal_data)
        mean_val = np.mean(signal_data)
        
        if std_dev < 0.1:
            return "dc_signal"
        elif dominant_freq > 0 and std_dev > 0.5:
            return "ac_signal"
        elif std_dev > 1.0:
            return "noisy_signal"
        else:
            return "mixed_signal"
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        生成测试建议
        
        @param {dict} analysis - 分析结果
        @returns {list} 建议列表
        """
        recommendations = []
        
        signal_type = analysis.get("signal_type", "unknown")
        amplitude = analysis.get("amplitude", {})
        
        if signal_type == "noisy_signal":
            recommendations.append("信号噪声较高，建议检查接地和屏蔽")
            recommendations.append("考虑使用低通滤波器减少高频噪声")
        
        if amplitude.get("peak_to_peak", 0) > 5.0:
            recommendations.append("信号幅度较大，注意示波器输入保护")
        
        if amplitude.get("rms", 0) < 0.1:
            recommendations.append("信号幅度较小，建议增加垂直灵敏度")
        
        return recommendations
    
    def _generate_test_workflow(self, objective: str, signal_type: str) -> List[Dict[str, Any]]:
        """
        生成测试工作流程
        
        @param {str} objective - 测试目标
        @param {str} signal_type - 信号类型
        @returns {list} 工作流程步骤
        """
        workflow = [
            {
                "step": 1,
                "action": "设备连接",
                "description": "连接示波器并检查设备状态",
                "estimated_time": "30秒"
            },
            {
                "step": 2,
                "action": "信号连接",
                "description": "连接被测信号到示波器输入端",
                "estimated_time": "1分钟"
            },
            {
                "step": 3,
                "action": "参数配置",
                "description": f"根据{signal_type}信号特点配置示波器参数",
                "estimated_time": "2分钟"
            },
            {
                "step": 4,
                "action": "数据采集",
                "description": "开始信号采集并观察波形",
                "estimated_time": "5分钟"
            },
            {
                "step": 5,
                "action": "自动测量",
                "description": f"执行{objective}相关的自动测量",
                "estimated_time": "3分钟"
            },
            {
                "step": 6,
                "action": "结果分析",
                "description": "分析测量结果并生成报告",
                "estimated_time": "5分钟"
            }
        ]
        
        return workflow
    
    def _process_user_query(self, query: str, context: Dict[str, Any]) -> str:
        """
        处理用户查询
        
        @param {str} query - 用户查询
        @param {dict} context - 上下文信息
        @returns {str} AI回复
        """
        # 简单的关键词匹配回复（实际应用中使用LangChain）
        query_lower = query.lower()
        
        if "频谱" in query or "频域" in query:
            return "频谱分析可以帮助您了解信号的频率成分。建议使用FFT功能进行频域分析，注意选择合适的窗函数以减少频谱泄漏。"
        
        elif "噪声" in query:
            return "噪声分析需要关注信噪比和噪声类型。建议检查接地连接，使用差分探头，并考虑信号源的质量。"
        
        elif "测量" in query:
            return "自动测量功能可以快速获得信号参数。建议先稳定触发，然后选择合适的测量项目，如幅度、频率、占空比等。"
        
        elif "触发" in query:
            return "正确的触发设置是稳定显示的关键。建议根据信号特点选择边沿触发、脉宽触发或视频触发模式。"
        
        else:
            return "我可以帮助您进行信号分析、测量指导和故障诊断。请具体描述您遇到的问题或需要的帮助。"
    
    def _diagnose_signal_issues(self, signal_data: List[float], symptoms: List[str]) -> Dict[str, Any]:
        """
        诊断信号问题
        
        @param {list} signal_data - 信号数据
        @param {list} symptoms - 症状描述
        @returns {dict} 诊断结果
        """
        issues = []
        solutions = []
        
        for symptom in symptoms:
            if "不稳定" in symptom or "抖动" in symptom:
                issues.append("信号抖动")
                solutions.append("检查触发设置和信号源稳定性")
            
            elif "失真" in symptom:
                issues.append("信号失真")
                solutions.append("检查探头补偿和输入阻抗匹配")
            
            elif "噪声" in symptom:
                issues.append("噪声干扰")
                solutions.append("改善接地和屏蔽，检查电源质量")
        
        return {
            "identified_issues": issues,
            "recommended_solutions": solutions,
            "confidence": 0.8
        }
    
    def _generate_test_report(self, test_results: Dict[str, Any], template: str) -> Dict[str, Any]:
        """
        生成测试报告
        
        @param {dict} test_results - 测试结果
        @param {str} template - 报告模板
        @returns {dict} 报告内容
        """
        return {
            "title": "示波器测试报告",
            "timestamp": "2024-01-01 12:00:00",
            "summary": "测试已完成，所有参数在正常范围内",
            "details": test_results,
            "recommendations": [
                "定期校准设备以确保测量精度",
                "保持良好的测试环境和接地条件"
            ]
        }
    
    def _send_task_result(self, task_id: str, result: Dict[str, Any]):
        """
        发送任务结果
        
        @param {str} task_id - 任务ID
        @param {dict} result - 结果数据
        """
        message = {
            "type": "task_completed",
            "data": {
                "task_id": task_id,
                "result": result,
                "source": "ai_actor"
            }
        }
        
        self.send_to_system_manager(message)
        self.logger.info(f"任务 {task_id} 完成")
    
    def get_ai_status(self) -> str:
        """
        获取AI状态
        
        @returns {str} AI状态
        """
        return self.ai_status 