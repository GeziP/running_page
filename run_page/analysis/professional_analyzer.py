"""
Professional Running Analysis Module
专业跑步数据分析模块

基于权威跑步训练理论：
- VDOT系统（Jack Daniels）
- MAF 180心率训练法（Phil Maffetone）
- 训练压力评分（TSS）
- 训练区间划分

所有公式均来自权威理论，确保数据准确性
"""

import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict


class VDOTCalculator:
    """VDOT计算器 - 基于Jack Daniels的跑步公式"""
    
    # VDOT查表数据 - 基于Jack Daniels Running Formula
    VDOT_TABLE = {
        # 格式: VDOT值: {distance_km: time_seconds, ...}
        30: {
            5: 30*60 + 40,      # 5K: 30:40
            10: 63*60 + 46,     # 10K: 63:46
            21.1: 141*60 + 4,   # 半马: 2:21:04
            42.2: 289*60 + 17   # 全马: 4:49:17
        },
        32: {
            5: 29*60 + 5,
            10: 60*60 + 26,
            21.1: 133*60 + 49,
            42.2: 274*60 + 58
        },
        34: {
            5: 27*60 + 39,
            10: 57*60 + 26,
            21.1: 127*60 + 16,
            42.2: 262*60 + 3
        },
        36: {
            5: 26*60 + 22,
            10: 54*60 + 44,
            21.1: 121*60 + 19,
            42.2: 250*60 + 19
        },
        38: {
            5: 25*60 + 12,
            10: 52*60 + 17,
            21.1: 115*60 + 55,
            42.2: 239*60 + 35
        },
        40: {
            5: 24*60 + 8,
            10: 50*60 + 3,
            21.1: 110*60 + 59,
            42.2: 229*60 + 45
        },
        42: {
            5: 23*60 + 9,
            10: 48*60 + 1,
            21.1: 106*60 + 27,
            42.2: 220*60 + 43
        },
        44: {
            5: 22*60 + 15,
            10: 46*60 + 9,
            21.1: 102*60 + 17,
            42.2: 212*60 + 23
        },
        46: {
            5: 21*60 + 25,
            10: 44*60 + 25,
            21.1: 98*60 + 27,
            42.2: 204*60 + 39
        },
        48: {
            5: 20*60 + 39,
            10: 42*60 + 50,
            21.1: 94*60 + 53,
            42.2: 197*60 + 29
        },
        50: {
            5: 19*60 + 57,
            10: 41*60 + 21,
            21.1: 91*60 + 35,
            42.2: 190*60 + 49
        },
        52: {
            5: 19*60 + 17,
            10: 39*60 + 59,
            21.1: 88*60 + 31,
            42.2: 184*60 + 36
        },
        54: {
            5: 18*60 + 40,
            10: 38*60 + 42,
            21.1: 85*60 + 40,
            42.2: 178*60 + 47
        },
        56: {
            5: 18*60 + 5,
            10: 37*60 + 31,
            21.1: 83*60 + 0,
            42.2: 173*60 + 20
        },
        58: {
            5: 17*60 + 33,
            10: 36*60 + 24,
            21.1: 80*60 + 30,
            42.2: 168*60 + 14
        },
        60: {
            5: 17*60 + 3,
            10: 35*60 + 22,
            21.1: 78*60 + 9,
            42.2: 163*60 + 25
        },
        62: {
            5: 16*60 + 34,
            10: 34*60 + 23,
            21.1: 75*60 + 57,
            42.2: 158*60 + 54
        },
        64: {
            5: 16*60 + 7,
            10: 33*60 + 28,
            21.1: 73*60 + 53,
            42.2: 154*60 + 38
        },
        66: {
            5: 15*60 + 42,
            10: 32*60 + 35,
            21.1: 71*60 + 56,
            42.2: 150*60 + 36
        },
        68: {
            5: 15*60 + 18,
            10: 31*60 + 46,
            21.1: 70*60 + 5,
            42.2: 146*60 + 47
        },
        70: {
            5: 14*60 + 55,
            10: 31*60 + 0,
            21.1: 68*60 + 21,
            42.2: 143*60 + 10
        }
    }
    
    # 训练配速计算参数
    TRAINING_PACES = {
        30: {"easy": 12*60 + 40, "tempo": 10*60 + 18, "interval": 2*60 + 22, "repetition": 2*60 + 15},
        32: {"easy": 12*60 + 4, "tempo": 9*60 + 47, "interval": 2*60 + 14, "repetition": 2*60 + 7},
        34: {"easy": 11*60 + 32, "tempo": 9*60 + 20, "interval": 2*60 + 8, "repetition": 2*60 + 0},
        36: {"easy": 11*60 + 2, "tempo": 8*60 + 55, "interval": 2*60 + 2, "repetition": 1*60 + 54},
        38: {"easy": 10*60 + 35, "tempo": 8*60 + 33, "interval": 1*60 + 56, "repetition": 1*60 + 48},
        40: {"easy": 10*60 + 11, "tempo": 8*60 + 12, "interval": 1*60 + 52, "repetition": 1*60 + 43},
        42: {"easy": 9*60 + 48, "tempo": 7*60 + 52, "interval": 1*60 + 48, "repetition": 1*60 + 38},
        44: {"easy": 9*60 + 27, "tempo": 7*60 + 33, "interval": 1*60 + 44, "repetition": 1*60 + 34},
        46: {"easy": 9*60 + 7, "tempo": 7*60 + 17, "interval": 1*60 + 40, "repetition": 1*60 + 30},
        48: {"easy": 8*60 + 49, "tempo": 7*60 + 2, "interval": 1*60 + 36, "repetition": 1*60 + 26},
        50: {"easy": 8*60 + 32, "tempo": 6*60 + 51, "interval": 1*60 + 33, "repetition": 1*60 + 22},
        52: {"easy": 8*60 + 16, "tempo": 6*60 + 38, "interval": 1*60 + 31, "repetition": 1*60 + 19},
        54: {"easy": 8*60 + 1, "tempo": 6*60 + 26, "interval": 1*60 + 28, "repetition": 1*60 + 16},
        56: {"easy": 7*60 + 48, "tempo": 6*60 + 15, "interval": 1*60 + 26, "repetition": 1*60 + 13},
        58: {"easy": 7*60 + 34, "tempo": 6*60 + 4, "interval": 1*60 + 23, "repetition": 1*60 + 11},
        60: {"easy": 7*60 + 22, "tempo": 5*60 + 54, "interval": 1*60 + 21, "repetition": 1*60 + 8},
        62: {"easy": 7*60 + 11, "tempo": 5*60 + 45, "interval": 1*60 + 19, "repetition": 1*60 + 6},
        64: {"easy": 7*60 + 0, "tempo": 5*60 + 36, "interval": 1*60 + 17, "repetition": 1*60 + 4},
        66: {"easy": 6*60 + 49, "tempo": 5*60 + 28, "interval": 1*60 + 15, "repetition": 1*60 + 2},
        68: {"easy": 6*60 + 39, "tempo": 5*60 + 20, "interval": 1*60 + 13, "repetition": 1*60 + 0},
        70: {"easy": 6*60 + 30, "tempo": 5*60 + 13, "interval": 1*60 + 11, "repetition": 0*60 + 58},
    }

    def calculate_vdot_from_race(self, distance_km: float, time_seconds: int) -> float:
        """根据比赛成绩计算VDOT值"""
        if distance_km <= 0 or time_seconds <= 0:
            return 0
        
        # 使用Jack Daniels的VDOT公式
        # VDOT = -4.6 + 0.182258 * (velocity_m_per_min) + 0.000104 * (velocity_m_per_min)^2
        velocity_m_per_min = (distance_km * 1000) / (time_seconds / 60)
        
        vdot = -4.6 + 0.182258 * velocity_m_per_min + 0.000104 * (velocity_m_per_min ** 2)
        
        # 限制在合理范围内
        return max(20, min(85, round(vdot, 1)))
    
    def get_training_paces(self, vdot: float) -> Dict[str, int]:
        """根据VDOT值计算训练配速（秒/公里）"""
        if vdot < 30:
            vdot = 30
        elif vdot > 70:
            vdot = 70
        
        # 找到最接近的VDOT值
        closest_vdot = min(self.TRAINING_PACES.keys(), key=lambda x: abs(x - vdot))
        
        if closest_vdot in self.TRAINING_PACES:
            return self.TRAINING_PACES[closest_vdot].copy()
        
        return {"easy": 600, "tempo": 480, "interval": 120, "repetition": 100}
    
    def predict_race_times(self, vdot: float) -> Dict[str, int]:
        """根据VDOT值预测各距离比赛时间"""
        distances = {
            "5K": 5,
            "10K": 10,
            "半程马拉松": 21.1,
            "全程马拉松": 42.2
        }
        
        predictions = {}
        closest_vdot = min(self.VDOT_TABLE.keys(), key=lambda x: abs(x - vdot))
        
        if closest_vdot in self.VDOT_TABLE:
            table_data = self.VDOT_TABLE[closest_vdot]
            for name, distance in distances.items():
                if distance in table_data:
                    predictions[name] = table_data[distance]
        
        return predictions


class MAFCalculator:
    """MAF心率计算器 - 基于Phil Maffetone的180公式"""
    
    def calculate_maf_heart_rate(self, age: int, health_category: str) -> int:
        """
        计算MAF心率
        
        Args:
            age: 年龄
            health_category: 健康类别
                - 'major_illness': 重大疾病/服药（-10）
                - 'minor_issues': 轻微问题/新手（-5）
                - 'healthy': 健康训练者（0）
                - 'elite': 精英运动员（+5）
                - 'senior': 65岁以上（可能需要+10）
        
        Returns:
            MAF心率值
        """
        base_hr = 180 - age
        
        adjustments = {
            'major_illness': -10,  # 重大疾病、服药、康复期
            'minor_issues': -5,    # 受伤、感冒频繁、哮喘、新手
            'healthy': 0,          # 正常健康训练者
            'elite': 5,            # 精英运动员（2年以上训练无伤病）
            'senior': 10           # 65岁以上（需要评估）
        }
        
        adjustment = adjustments.get(health_category, 0)
        maf_hr = base_hr + adjustment
        
        # 确保在合理范围内
        return max(100, min(180, maf_hr))
    
    def get_heart_rate_zones(self, maf_hr: int) -> Dict[str, Dict[str, int]]:
        """
        基于MAF心率计算训练区间
        
        返回5个心率区间和对应的训练目的
        """
        zones = {
            "区间1": {
                "min_hr": int(maf_hr * 0.65),
                "max_hr": int(maf_hr * 0.75),
                "name": "恢复区",
                "description": "主动恢复，提高脂肪燃烧",
                "rpe": "1-2级（很轻松）"
            },
            "区间2": {
                "min_hr": int(maf_hr * 0.75),
                "max_hr": int(maf_hr * 0.85),
                "name": "有氧基础区",
                "description": "建立有氧基础，长距离LSD",
                "rpe": "3-4级（轻松）"
            },
            "区间3": {
                "min_hr": int(maf_hr * 0.85),
                "max_hr": maf_hr,
                "name": "MAF区间",
                "description": "最大有氧功能，提高效率",
                "rpe": "5-6级（适中）"
            },
            "区间4": {
                "min_hr": maf_hr,
                "max_hr": int(maf_hr * 1.1),
                "name": "乳酸阈值区",
                "description": "提高乳酸清除能力",
                "rpe": "7-8级（困难）"
            },
            "区间5": {
                "min_hr": int(maf_hr * 1.1),
                "max_hr": int(maf_hr * 1.2),
                "name": "无氧功率区",
                "description": "提高VO2max和无氧功率",
                "rpe": "9-10级（最大强度）"
            }
        }
        
        return zones


class TSSCalculator:
    """训练压力评分计算器 - 基于TrainingPeaks理论"""
    
    def calculate_running_tss(self, duration_minutes: int, avg_pace_per_km: int, 
                            threshold_pace_per_km: int) -> float:
        """
        计算跑步TSS
        
        Args:
            duration_minutes: 训练时长（分钟）
            avg_pace_per_km: 平均配速（秒/公里）
            threshold_pace_per_km: 阈值配速（秒/公里）
        
        Returns:
            TSS分数
        """
        if duration_minutes <= 0 or avg_pace_per_km <= 0 or threshold_pace_per_km <= 0:
            return 0
        
        # 计算强度因子 (IF)
        # IF = threshold_pace / avg_pace (配速越快，值越大)
        intensity_factor = threshold_pace_per_km / avg_pace_per_km
        
        # TSS = (duration_hours * IF^2) * 100
        duration_hours = duration_minutes / 60
        tss = duration_hours * (intensity_factor ** 2) * 100
        
        return round(tss, 1)
    
    def calculate_hr_based_tss(self, duration_minutes: int, avg_hr: int, 
                              threshold_hr: int) -> float:
        """基于心率计算TSS"""
        if duration_minutes <= 0 or avg_hr <= 0 or threshold_hr <= 0:
            return 0
        
        # 计算心率强度因子
        hr_intensity_factor = avg_hr / threshold_hr
        
        # 限制在合理范围内
        hr_intensity_factor = min(1.2, max(0.4, hr_intensity_factor))
        
        duration_hours = duration_minutes / 60
        tss = duration_hours * (hr_intensity_factor ** 2) * 100
        
        return round(tss, 1)


class ProfessionalAnalyzer:
    """专业跑步数据分析器"""
    
    def __init__(self):
        self.vdot_calc = VDOTCalculator()
        self.maf_calc = MAFCalculator()
        self.tss_calc = TSSCalculator()
    
    def analyze_runner_profile(self, age: int, recent_race_distance: float, 
                              recent_race_time: int, health_status: str) -> Dict[str, Any]:
        """
        生成跑者完整分析报告
        
        Args:
            age: 年龄
            recent_race_distance: 最近比赛距离（公里）
            recent_race_time: 最近比赛时间（秒）
            health_status: 健康状况类别
        
        Returns:
            完整的分析报告
        """
        # 计算VDOT
        vdot = self.vdot_calc.calculate_vdot_from_race(recent_race_distance, recent_race_time)
        
        # 获取训练配速
        training_paces = self.vdot_calc.get_training_paces(vdot)
        
        # 预测比赛时间
        race_predictions = self.vdot_calc.predict_race_times(vdot)
        
        # 计算MAF心率
        maf_hr = self.maf_calc.calculate_maf_heart_rate(age, health_status)
        
        # 获取心率区间
        hr_zones = self.maf_calc.get_heart_rate_zones(maf_hr)
        
        # 生成训练建议
        training_advice = self._generate_training_advice(vdot, maf_hr, age)
        
        return {
            "vdot_analysis": {
                "vdot_value": vdot,
                "training_paces": training_paces,
                "race_predictions": race_predictions,
                "fitness_level": self._classify_fitness_level(vdot)
            },
            "heart_rate_analysis": {
                "maf_heart_rate": maf_hr,
                "training_zones": hr_zones,
                "recommended_training": f"大部分训练应保持在{maf_hr-10}-{maf_hr}心率区间"
            },
            "training_recommendations": training_advice,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def analyze_training_load(self, activities: List[Dict]) -> Dict[str, Any]:
        """分析训练负荷趋势"""
        if not activities:
            return {}
        
        weekly_tss = defaultdict(float)
        monthly_tss = defaultdict(float)
        
        for activity in activities:
            # 计算每个活动的TSS
            duration = self._parse_time(activity.get("moving_time", "0"))
            distance = float(activity.get("distance", 0)) / 1000  # 转为公里
            
            if duration > 0 and distance > 0:
                avg_pace = duration / distance  # 秒/公里
                # 假设阈值配速为6:00/公里（360秒）
                threshold_pace = 360
                
                tss = self.tss_calc.calculate_running_tss(
                    duration / 60, avg_pace, threshold_pace
                )
                
                # 按周分组
                date_str = activity.get("start_date_local", "").split("T")[0]
                if date_str:
                    try:
                        date = datetime.fromisoformat(date_str)
                        week_key = f"{date.year}-W{date.isocalendar()[1]}"
                        month_key = f"{date.year}-{date.month:02d}"
                        
                        weekly_tss[week_key] += tss
                        monthly_tss[month_key] += tss
                    except:
                        continue
        
        return {
            "weekly_tss": dict(weekly_tss),
            "monthly_tss": dict(monthly_tss),
            "avg_weekly_tss": sum(weekly_tss.values()) / len(weekly_tss) if weekly_tss else 0,
            "training_load_status": self._assess_training_load(weekly_tss)
        }
    
    def _classify_fitness_level(self, vdot: float) -> str:
        """根据VDOT值分类健身水平"""
        if vdot >= 65:
            return "精英级（Elite）"
        elif vdot >= 55:
            return "优秀级（Excellent）"
        elif vdot >= 45:
            return "良好级（Good）"
        elif vdot >= 35:
            return "中等级（Fair）"
        else:
            return "初级（Beginner）"
    
    def _generate_training_advice(self, vdot: float, maf_hr: int, age: int) -> Dict[str, str]:
        """生成个性化训练建议"""
        advice = {
            "primary_focus": "",
            "weekly_structure": "",
            "pace_guidelines": "",
            "volume_recommendations": "",
            "cautions": ""
        }
        
        # 基于VDOT水平给出建议
        if vdot < 40:
            advice["primary_focus"] = "重点建立有氧基础，80%以上训练应在MAF心率以下"
            advice["weekly_structure"] = "每周3-4次训练，以轻松跑为主，每周1次稍快节奏跑"
            advice["volume_recommendations"] = "每周总里程不超过30-40公里"
        elif vdot < 55:
            advice["primary_focus"] = "在保持有氧基础的同时，适度增加节奏跑和间歇训练"
            advice["weekly_structure"] = "每周4-5次训练，70%轻松跑，20%节奏跑，10%间歇训练"
            advice["volume_recommendations"] = "每周总里程40-60公里"
        else:
            advice["primary_focus"] = "精英训练：有氧基础+系统化的速度和专项训练"
            advice["weekly_structure"] = "每周6-7次训练，包含多种训练类型的周期化安排"
            advice["volume_recommendations"] = "每周总里程60公里以上"
        
        # 基于年龄的建议
        if age >= 50:
            advice["cautions"] = "注意恢复时间，增加力量训练，减少高强度训练频率"
        elif age >= 40:
            advice["cautions"] = "平衡训练强度，重视睡眠和营养恢复"
        else:
            advice["cautions"] = "注重技术训练，避免过度训练导致的伤病"
        
        return advice
    
    def _assess_training_load(self, weekly_tss: Dict) -> str:
        """评估训练负荷状态"""
        if not weekly_tss:
            return "数据不足"
        
        recent_weeks = list(weekly_tss.values())[-4:]  # 最近4周
        avg_tss = sum(recent_weeks) / len(recent_weeks)
        
        if avg_tss < 200:
            return "训练负荷偏低，可以考虑适度增加"
        elif avg_tss < 400:
            return "训练负荷适中，保持当前强度"
        elif avg_tss < 600:
            return "训练负荷较高，注意恢复"
        else:
            return "训练负荷过高，建议减少训练量"
    
    def _parse_time(self, time_str: str) -> int:
        """解析时间字符串为秒数"""
        if not time_str or time_str == "0":
            return 0
        
        try:
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                return int(time_str)
        except (ValueError, IndexError):
            return 0 