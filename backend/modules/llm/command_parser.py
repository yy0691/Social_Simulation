"""
指令解析模块
用于解析和处理玩家输入的各种指令
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class CommandType(Enum):
    """指令类型枚举"""
    COMMUNITY_ACTION = "community_action"      # 社群行动类指令
    ECONOMIC_POLICY = "economic_policy"        # 经济政策类指令  
    SOCIAL_EVENT = "social_event"              # 社会事件类指令
    EDUCATION_INITIATIVE = "education_initiative"  # 教育倡议类指令
    HEALTH_PROGRAM = "health_program"          # 健康项目类指令
    INFRASTRUCTURE = "infrastructure"          # 基础设施类指令
    EMERGENCY_RESPONSE = "emergency_response"  # 紧急响应类指令
    RESEARCH_PROJECT = "research_project"      # 研究项目类指令
    UNKNOWN = "unknown"                        # 未知类指令

@dataclass 
class ParsedCommand:
    """解析后的指令数据类"""
    original_text: str
    command_type: CommandType
    action: str
    targets: List[str]
    parameters: Dict[str, Any]
    urgency: int  # 1-5，紧急程度
    expected_impact: Dict[str, int]  # 预期对各项指标的影响
    confidence: float  # 解析置信度 0-1

class CommandParser:
    """指令解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.command_patterns = self._init_command_patterns()
        self.action_keywords = self._init_action_keywords()
    
    def _init_command_patterns(self) -> Dict[CommandType, List[str]]:
        """初始化指令模式正则表达式"""
        patterns = {
            CommandType.COMMUNITY_ACTION: [
                r"组织|举办|开展|发起|启动.*?(活动|聚会|庆祝|节日|比赛)",
                r"建立|创建|成立.*?(组织|团体|社团|俱乐部)",
                r"改善|提升|增强.*?(社区|氛围|环境|关系)"
            ],
            CommandType.ECONOMIC_POLICY: [
                r"(增加|减少|调整).*?(税收|补贴|工资|价格|投资)",
                r"(制定|实施|修改).*?(经济|财政|金融).*?政策",
                r"(开设|关闭|扩大).*?(商店|市场|工厂|企业)"
            ],
            CommandType.SOCIAL_EVENT: [
                r"(举行|召开|组织).*?(会议|大会|集会|论坛)",
                r"(庆祝|纪念|哀悼).*?(节日|纪念日|事件)",
                r"(解决|处理|调解).*?(冲突|纠纷|争议)"
            ],
            CommandType.EDUCATION_INITIATIVE: [
                r"(建设|改善|升级).*?(学校|教育|培训)",
                r"(开设|增加|取消).*?(课程|课堂|培训)",
                r"(提高|改善|加强).*?(教育|学习|知识)"
            ],
            CommandType.HEALTH_PROGRAM: [
                r"(建设|改善|升级).*?(医院|诊所|卫生)",
                r"(开展|实施|推广).*?(健康|医疗|卫生).*?计划",
                r"(预防|治疗|控制).*?(疾病|传染病|健康问题)"
            ],
            CommandType.INFRASTRUCTURE: [
                r"(建设|修建|改善).*?(道路|桥梁|建筑|设施)",
                r"(升级|维护|修复).*?(基础设施|公共设施)",
                r"(安装|建立|完善).*?(水电|通信|交通)"
            ],
            CommandType.EMERGENCY_RESPONSE: [
                r"(应对|处理|解决).*?(紧急|危机|灾难|事故)",
                r"(撤离|救援|援助|支持).*?(居民|灾民|受害者)",
                r"(宣布|进入|解除).*?(紧急状态|戒严|警报)"
            ],
            CommandType.RESEARCH_PROJECT: [
                r"(开展|启动|推进).*?(研究|调查|实验|项目)",
                r"(发明|创新|开发).*?(技术|产品|方法)",
                r"(探索|发现|研究).*?(科学|知识|真理)"
            ]
        }
        return patterns
    
    def _init_action_keywords(self) -> Dict[str, Dict[str, int]]:
        """初始化行动关键词及其对社群指标的预期影响"""
        return {
            # 积极行动
            "庆祝": {"happiness": 15, "health": 5, "education": 0, "economy": -5},
            "节日": {"happiness": 20, "health": 0, "education": 0, "economy": 10},
            "聚会": {"happiness": 10, "health": -5, "education": 5, "economy": 5},
            "建设": {"happiness": 5, "health": 10, "education": 5, "economy": -10},
            "教育": {"happiness": 5, "health": 0, "education": 15, "economy": -5},
            "医疗": {"happiness": 10, "health": 20, "education": 0, "economy": -10},
            "投资": {"happiness": -5, "health": 0, "education": 0, "economy": 15},
            "创新": {"happiness": 5, "health": 0, "education": 10, "economy": 10},
            
            # 消极/困难行动
            "税收": {"happiness": -10, "health": 0, "education": 0, "economy": 10},
            "紧急": {"happiness": -15, "health": -10, "education": 0, "economy": -5},
            "危机": {"happiness": -20, "health": -15, "education": -5, "economy": -15},
            "冲突": {"happiness": -25, "health": -10, "education": -10, "economy": -10},
            "灾难": {"happiness": -30, "health": -25, "education": -5, "economy": -20},
            
            # 中性行动
            "会议": {"happiness": -5, "health": 0, "education": 5, "economy": 0},
            "调查": {"happiness": 0, "health": 0, "education": 10, "economy": 0},
            "维护": {"happiness": 0, "health": 5, "education": 0, "economy": -5},
        }
    
    def parse_command(self, command_text: str) -> ParsedCommand:
        """
        解析指令文本
        
        Args:
            command_text: 原始指令文本
            
        Returns:
            ParsedCommand: 解析后的指令对象
        """
        command_text = command_text.strip()
        
        # 检测指令类型
        command_type = self._detect_command_type(command_text)
        
        # 提取行动和目标
        action, targets = self._extract_action_and_targets(command_text)
        
        # 提取参数
        parameters = self._extract_parameters(command_text)
        
        # 评估紧急程度
        urgency = self._assess_urgency(command_text)
        
        # 预测影响
        expected_impact = self._predict_impact(command_text, action)
        
        # 计算置信度
        confidence = self._calculate_confidence(command_text, command_type, action)
        
        return ParsedCommand(
            original_text=command_text,
            command_type=command_type,
            action=action,
            targets=targets,
            parameters=parameters,
            urgency=urgency,
            expected_impact=expected_impact,
            confidence=confidence
        )
    
    def _detect_command_type(self, text: str) -> CommandType:
        """检测指令类型"""
        text_lower = text.lower()
        
        max_matches = 0
        best_type = CommandType.UNKNOWN
        
        for cmd_type, patterns in self.command_patterns.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    matches += 1
            
            if matches > max_matches:
                max_matches = matches
                best_type = cmd_type
        
        return best_type
    
    def _extract_action_and_targets(self, text: str) -> Tuple[str, List[str]]:
        """提取行动词和目标对象"""
        # 常见行动词
        action_verbs = [
            "建设", "建立", "建造", "修建", "组织", "举办", "开展", "发起",
            "启动", "实施", "推行", "执行", "制定", "调整", "改善", "提升",
            "增加", "减少", "取消", "关闭", "开设", "创建", "成立", "解决",
            "处理", "应对", "预防", "治疗", "控制", "维护", "修复", "升级"
        ]
        
        # 查找行动词
        action = "执行"  # 默认行动
        for verb in action_verbs:
            if verb in text:
                action = verb
                break
        
        # 查找目标对象
        target_nouns = [
            "活动", "聚会", "节日", "庆祝", "比赛", "会议", "学校", "医院",
            "道路", "桥梁", "公园", "市场", "工厂", "住房", "设施", "社区",
            "居民", "政策", "法律", "规则", "计划", "项目", "研究", "投资"
        ]
        
        targets = []
        for noun in target_nouns:
            if noun in text:
                targets.append(noun)
        
        return action, targets
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """提取指令参数"""
        parameters = {}
        
        # 提取数字参数
        numbers = re.findall(r'\d+', text)
        if numbers:
            parameters["numbers"] = [int(n) for n in numbers]
        
        # 提取时间参数
        time_patterns = [
            r'(\d+)(天|日|周|月|年)',
            r'(今天|明天|下周|下月|明年)',
            r'(立即|马上|尽快|紧急)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            if matches:
                parameters["time_references"] = matches
                break
        
        # 提取强度词
        intensity_words = {
            "轻微": 1, "稍微": 1, "略微": 1,
            "适当": 2, "一般": 2, "正常": 2,
            "大幅": 3, "显著": 3, "明显": 3,
            "极大": 4, "巨大": 4, "彻底": 4,
            "完全": 5, "全面": 5, "彻底": 5
        }
        
        for word, intensity in intensity_words.items():
            if word in text:
                parameters["intensity"] = intensity
                break
        else:
            parameters["intensity"] = 2  # 默认强度
        
        return parameters
    
    def _assess_urgency(self, text: str) -> int:
        """评估指令紧急程度 (1-5)"""
        urgency_keywords = {
            5: ["紧急", "立即", "马上", "危机", "灾难", "严重"],
            4: ["尽快", "急需", "重要", "关键", "迫切"],
            3: ["及时", "必要", "应该", "需要"],
            2: ["适当", "考虑", "建议", "可以"],
            1: ["将来", "以后", "有空", "有时间"]
        }
        
        for urgency_level in range(5, 0, -1):
            for keyword in urgency_keywords[urgency_level]:
                if keyword in text:
                    return urgency_level
        
        return 2  # 默认紧急程度
    
    def _predict_impact(self, text: str, action: str) -> Dict[str, int]:
        """预测指令对各项指标的影响"""
        impact = {"happiness": 0, "health": 0, "education": 0, "economy": 0}
        
        # 基于行动词预测
        if action in self.action_keywords:
            base_impact = self.action_keywords[action].copy()
        else:
            # 基于关键词预测
            base_impact = {"happiness": 0, "health": 0, "education": 0, "economy": 0}
            for keyword, keyword_impact in self.action_keywords.items():
                if keyword in text:
                    for stat, value in keyword_impact.items():
                        base_impact[stat] += value
        
        # 根据强度调整
        intensity = 1.0
        if "大幅" in text or "显著" in text:
            intensity = 1.5
        elif "轻微" in text or "稍微" in text:
            intensity = 0.5
        elif "极大" in text or "巨大" in text:
            intensity = 2.0
        
        # 应用强度调整
        for stat in impact:
            impact[stat] = int(base_impact[stat] * intensity)
            # 限制影响范围在-50到50之间
            impact[stat] = max(-50, min(50, impact[stat]))
        
        return impact
    
    def _calculate_confidence(self, text: str, command_type: CommandType, action: str) -> float:
        """计算解析置信度"""
        confidence = 0.0
        
        # 基础置信度
        if command_type != CommandType.UNKNOWN:
            confidence += 0.3
        
        # 行动词匹配
        if action != "执行":
            confidence += 0.3
        
        # 文本清晰度
        if len(text) > 5:
            confidence += 0.2
        
        # 关键词匹配
        keyword_matches = 0
        for keywords in self.action_keywords.keys():
            if keywords in text:
                keyword_matches += 1
        
        if keyword_matches > 0:
            confidence += min(0.2, keyword_matches * 0.1)
        
        return min(1.0, confidence)
    
    def validate_command(self, parsed_command: ParsedCommand) -> Tuple[bool, str]:
        """
        验证解析后的指令是否有效
        
        Args:
            parsed_command: 解析后的指令
            
        Returns:
            tuple: (是否有效, 验证消息)
        """
        if parsed_command.confidence < 0.3:
            return False, "指令解析置信度过低，请提供更清晰的指令"
        
        if not parsed_command.original_text.strip():
            return False, "指令不能为空"
        
        if len(parsed_command.original_text) > 500:
            return False, "指令过长，请简化描述"
        
        if parsed_command.command_type == CommandType.UNKNOWN and parsed_command.confidence < 0.5:
            return False, "无法识别指令类型，请提供更具体的指令"
        
        return True, "指令验证通过"
    
    def get_command_suggestions(self, partial_text: str) -> List[str]:
        """根据部分文本提供指令建议"""
        suggestions = [
            "组织一次社区聚会活动",
            "建设新的医疗诊所",
            "开设职业技能培训课程", 
            "修建连接各区域的道路",
            "举办文化节庆祝活动",
            "实施环保政策改善环境",
            "创建青年创业扶持基金",
            "开展健康体检活动",
            "建立社区图书馆",
            "组织志愿者清洁活动"
        ]
        
        if not partial_text:
            return suggestions[:5]
        
        # 简单的文本匹配筛选
        partial_lower = partial_text.lower()
        filtered = []
        for suggestion in suggestions:
            if any(word in suggestion for word in partial_lower):
                filtered.append(suggestion)
        
        return filtered[:5] if filtered else suggestions[:5]

# 全局指令解析器实例
command_parser = CommandParser() 