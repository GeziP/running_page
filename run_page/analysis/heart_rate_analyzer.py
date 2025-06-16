"""
Heart Rate Analyzer
心率分析模块，提供心率区间、心率趋势等分析功能
"""

from typing import List, Dict, Any
from collections import defaultdict
from .activity_classifier import ActivityTypeManager

class HeartRateAnalyzer:
    """心率分析器"""
    
    def __init__(self):
        self.type_manager = ActivityTypeManager()
        # 心率区间定义（基于年龄和最大心率的百分比）
        self.hr_zones = {
            'zone1': (50, 60, '恢复区'),
            'zone2': (60, 70, '有氧基础区'),
            'zone3': (70, 80, '有氧发展区'),
            'zone4': (80, 90, '乳酸阈值区'),
            'zone5': (90, 100, '无氧能力区')
        }
    
    def analyze_heart_rate_trends(self, activities: List[Dict], activity_type: str = 'all') -> Dict:
        """
        分析心率趋势
        
        Args:
            activities: 活动列表
            activity_type: 活动类型
            
        Returns:
            心率趋势数据
        """
        filtered_activities = self.type_manager.filter_by_type(activities, activity_type)
        
        hr_data = []
        for activity in filtered_activities:
            avg_hr = activity.get('average_heartrate')
            if avg_hr and avg_hr > 0:
                hr_data.append({
                    'date': activity.get('start_date_local', '').split('T')[0],
                    'average_heartrate': float(avg_hr),
                    'activity_name': activity.get('name', ''),
                    'activity_id': activity.get('run_id'),
                    'activity_type': activity.get('type'),
                    'distance': float(activity.get('distance', 0)) / 1000
                })
        
        # 按日期排序
        hr_data.sort(key=lambda x: x['date'])
        
        return {
            'activity_type': activity_type,
            'heart_rate_data': hr_data,
            'summary': self._calculate_hr_summary(hr_data)
        }
    
    def analyze_heart_rate_zones(self, activities: List[Dict], max_hr: int = 190, activity_type: str = 'all') -> Dict:
        """
        分析心率区间分布
        
        Args:
            activities: 活动列表
            max_hr: 最大心率，默认190
            activity_type: 活动类型
            
        Returns:
            心率区间分析数据
        """
        filtered_activities = self.type_manager.filter_by_type(activities, activity_type)
        
        zone_distribution = defaultdict(int)
        total_activities_with_hr = 0
        
        for activity in filtered_activities:
            avg_hr = activity.get('average_heartrate')
            if avg_hr and avg_hr > 0:
                total_activities_with_hr += 1
                hr_percentage = (float(avg_hr) / max_hr) * 100
                
                # 确定属于哪个心率区间
                zone = self._classify_hr_zone(hr_percentage)
                zone_distribution[zone] += 1
        
        # 计算百分比
        zone_stats = {}
        for zone_key, (min_pct, max_pct, zone_name) in self.hr_zones.items():
            count = zone_distribution.get(zone_key, 0)
            percentage = (count / total_activities_with_hr * 100) if total_activities_with_hr > 0 else 0
            
            zone_stats[zone_key] = {
                'name': zone_name,
                'range': f"{min_pct}-{max_pct}%",
                'count': count,
                'percentage': round(percentage, 1)
            }
        
        return {
            'activity_type': activity_type,
            'max_heart_rate': max_hr,
            'total_activities_with_hr': total_activities_with_hr,
            'zone_distribution': zone_stats
        }
    
    def _calculate_hr_summary(self, hr_data: List[Dict]) -> Dict:
        """计算心率汇总统计"""
        if not hr_data:
            return {}
        
        heart_rates = [d['average_heartrate'] for d in hr_data]
        
        return {
            'total_activities': len(hr_data),
            'average_heart_rate': round(sum(heart_rates) / len(heart_rates), 1),
            'max_heart_rate': max(heart_rates),
            'min_heart_rate': min(heart_rates)
        }
    
    def _classify_hr_zone(self, hr_percentage: float) -> str:
        """根据心率百分比确定心率区间"""
        for zone_key, (min_pct, max_pct, _) in self.hr_zones.items():
            if min_pct <= hr_percentage < max_pct:
                return zone_key
        
        # 如果超出所有区间，归为最高区间
        return 'zone5' 