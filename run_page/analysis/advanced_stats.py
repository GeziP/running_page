"""
Advanced Statistics Analyzer
高级统计分析，包括配速趋势、心率分析、训练强度分析等
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import statistics
from .activity_classifier import ActivityTypeManager

class AdvancedStatsAnalyzer:
    """高级统计分析器"""
    
    def __init__(self):
        self.type_manager = ActivityTypeManager()
    
    def analyze_pace_trends(self, activities: List[Dict], activity_type: str = 'running') -> Dict:
        """
        分析配速趋势
        
        Args:
            activities: 活动列表
            activity_type: 活动类型
            
        Returns:
            配速趋势分析数据
        """
        # 仅分析跑步类活动
        if activity_type not in ['running', 'trail_running', 'all']:
            return {}
        
        filtered_activities = self.type_manager.filter_by_type(activities, activity_type)
        
        pace_data = []
        monthly_paces = defaultdict(list)
        
        for activity in filtered_activities:
            distance_km = float(activity.get('distance', 0)) / 1000
            time_seconds = self.type_manager._parse_time(activity.get('moving_time', '0'))
            date_str = activity.get('start_date_local', '')
            
            if distance_km > 1 and time_seconds > 0:  # 至少1公里才计算配速
                pace_per_km = time_seconds / distance_km
                date = self._parse_date(date_str)
                
                if date:
                    month_key = date.strftime('%Y-%m')
                    pace_data.append({
                        'date': date_str.split('T')[0],
                        'distance': distance_km,
                        'pace_seconds': pace_per_km,
                        'pace_formatted': self.type_manager.format_pace(distance_km, time_seconds),
                        'activity_name': activity.get('name', ''),
                        'activity_id': activity.get('run_id'),
                        'month': month_key
                    })
                    monthly_paces[month_key].append(pace_per_km)
        
        # 按日期排序
        pace_data.sort(key=lambda x: x['date'])
        
        # 计算月度平均配速趋势
        monthly_trends = {}
        for month, paces in monthly_paces.items():
            if paces:
                monthly_trends[month] = {
                    'avg_pace': statistics.mean(paces),
                    'best_pace': min(paces),
                    'worst_pace': max(paces),
                    'std_dev': statistics.stdev(paces) if len(paces) > 1 else 0,
                    'count': len(paces),
                    'improvement': 0  # 计算改进幅度
                }
        
        return {
            'activity_type': activity_type,
            'pace_data': pace_data,
            'monthly_trends': monthly_trends,
            'summary': self._calculate_pace_summary(pace_data),
            'insights': self._generate_pace_insights(pace_data, monthly_trends)
        }
    
    def analyze_heart_rate_zones(self, activities: List[Dict], max_hr: int = 190, activity_type: str = 'all') -> Dict:
        """
        分析心率区间分布
        
        Args:
            activities: 活动列表
            max_hr: 最大心率
            activity_type: 活动类型
            
        Returns:
            心率区间分析数据
        """
        filtered_activities = self.type_manager.filter_by_type(activities, activity_type)
        
        # 心率区间定义
        hr_zones = {
            'zone1': (50, 60, '恢复区', '#10B981'),  # 绿色
            'zone2': (60, 70, '有氧基础区', '#3B82F6'),  # 蓝色
            'zone3': (70, 80, '有氧发展区', '#F59E0B'),  # 黄色
            'zone4': (80, 90, '乳酸阈值区', '#EF4444'),  # 红色
            'zone5': (90, 100, '无氧能力区', '#8B5CF6')  # 紫色
        }
        
        zone_distribution = defaultdict(list)
        zone_time = defaultdict(int)
        total_activities_with_hr = 0
        hr_trends = defaultdict(list)
        
        for activity in filtered_activities:
            avg_hr = activity.get('average_heartrate')
            if avg_hr and avg_hr > 0:
                total_activities_with_hr += 1
                hr_percentage = (float(avg_hr) / max_hr) * 100
                time_seconds = self.type_manager._parse_time(activity.get('moving_time', '0'))
                date = self._parse_date(activity.get('start_date_local', ''))
                
                # 确定心率区间
                zone = self._classify_hr_zone(hr_percentage, hr_zones)
                zone_distribution[zone].append(float(avg_hr))
                zone_time[zone] += time_seconds
                
                if date:
                    month_key = date.strftime('%Y-%m')
                    hr_trends[month_key].append(float(avg_hr))
        
        # 计算区间统计
        zone_stats = {}
        total_time = sum(zone_time.values())
        
        for zone_key, (min_pct, max_pct, zone_name, color) in hr_zones.items():
            hrs = zone_distribution.get(zone_key, [])
            time_in_zone = zone_time.get(zone_key, 0)
            
            zone_stats[zone_key] = {
                'name': zone_name,
                'range': f"{min_pct}-{max_pct}% 最大心率",
                'hr_range': f"{int(max_hr * min_pct / 100)}-{int(max_hr * max_pct / 100)} bpm",
                'count': len(hrs),
                'percentage': round((len(hrs) / total_activities_with_hr * 100) if total_activities_with_hr > 0 else 0, 1),
                'time_percentage': round((time_in_zone / total_time * 100) if total_time > 0 else 0, 1),
                'avg_hr': round(statistics.mean(hrs), 1) if hrs else 0,
                'color': color
            }
        
        # 计算月度心率趋势
        monthly_hr_trends = {}
        for month, hrs in hr_trends.items():
            if hrs:
                monthly_hr_trends[month] = {
                    'avg_hr': round(statistics.mean(hrs), 1),
                    'max_hr': max(hrs),
                    'min_hr': min(hrs),
                    'count': len(hrs)
                }
        
        return {
            'activity_type': activity_type,
            'max_heart_rate': max_hr,
            'total_activities_with_hr': total_activities_with_hr,
            'zone_distribution': zone_stats,
            'monthly_trends': monthly_hr_trends,
            'insights': self._generate_hr_insights(zone_stats, monthly_hr_trends)
        }
    
    def analyze_training_load(self, activities: List[Dict], activity_type: str = 'all') -> Dict:
        """
        分析训练负荷
        
        Args:
            activities: 活动列表
            activity_type: 活动类型
            
        Returns:
            训练负荷分析数据
        """
        filtered_activities = self.type_manager.filter_by_type(activities, activity_type)
        
        weekly_load = defaultdict(lambda: {'distance': 0, 'time': 0, 'activities': 0, 'tss': 0})
        monthly_load = defaultdict(lambda: {'distance': 0, 'time': 0, 'activities': 0, 'tss': 0})
        
        for activity in filtered_activities:
            date = self._parse_date(activity.get('start_date_local', ''))
            if not date:
                continue
            
            distance_km = float(activity.get('distance', 0)) / 1000
            time_seconds = self.type_manager._parse_time(activity.get('moving_time', '0'))
            
            # 计算简化的训练压力分数 (TSS)
            # 基于距离和时间的简单公式
            tss = self._calculate_simple_tss(distance_km, time_seconds)
            
            # 周统计
            week_start = date - timedelta(days=date.weekday())
            week_key = week_start.strftime('%Y-W%U')
            weekly_load[week_key]['distance'] += distance_km
            weekly_load[week_key]['time'] += time_seconds
            weekly_load[week_key]['activities'] += 1
            weekly_load[week_key]['tss'] += tss
            
            # 月统计
            month_key = date.strftime('%Y-%m')
            monthly_load[month_key]['distance'] += distance_km
            monthly_load[month_key]['time'] += time_seconds
            monthly_load[month_key]['activities'] += 1
            monthly_load[month_key]['tss'] += tss
        
        # 计算负荷趋势和建议
        load_trends = self._analyze_load_trends(weekly_load, monthly_load)
        
        return {
            'activity_type': activity_type,
            'weekly_load': dict(weekly_load),
            'monthly_load': dict(monthly_load),
            'trends': load_trends,
            'recommendations': self._generate_training_recommendations(load_trends)
        }
    
    def analyze_performance_metrics(self, activities: List[Dict], activity_type: str = 'running') -> Dict:
        """
        分析表现指标
        
        Args:
            activities: 活动列表
            activity_type: 活动类型
            
        Returns:
            表现指标分析数据
        """
        filtered_activities = self.type_manager.filter_by_type(activities, activity_type)
        
        # 按距离分组分析
        distance_groups = {
            '5K': (4, 6),
            '10K': (9, 11),
            'Half': (20, 23),
            'Marathon': (40, 44)
        }
        
        performance_by_distance = {}
        
        for group_name, (min_km, max_km) in distance_groups.items():
            group_activities = [
                a for a in filtered_activities
                if min_km <= float(a.get('distance', 0)) / 1000 <= max_km
            ]
            
            if group_activities:
                paces = []
                speeds = []
                
                for activity in group_activities:
                    distance_km = float(activity.get('distance', 0)) / 1000
                    time_seconds = self.type_manager._parse_time(activity.get('moving_time', '0'))
                    
                    if distance_km > 0 and time_seconds > 0:
                        pace = time_seconds / distance_km
                        speed = float(activity.get('average_speed', 0))
                        paces.append(pace)
                        speeds.append(speed)
                
                if paces:
                    performance_by_distance[group_name] = {
                        'count': len(group_activities),
                        'best_pace': min(paces),
                        'avg_pace': statistics.mean(paces),
                        'worst_pace': max(paces),
                        'best_pace_formatted': self.type_manager.format_time(int(min(paces))),
                        'avg_pace_formatted': self.type_manager.format_time(int(statistics.mean(paces))),
                        'pace_improvement': self._calculate_pace_improvement(paces, group_activities),
                        'consistency': self._calculate_consistency(paces)
                    }
        
        return {
            'activity_type': activity_type,
            'performance_by_distance': performance_by_distance,
            'overall_trends': self._analyze_overall_performance_trends(filtered_activities)
        }
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    def _classify_hr_zone(self, hr_percentage: float, hr_zones: Dict) -> str:
        """根据心率百分比确定心率区间"""
        for zone_key, (min_pct, max_pct, _, _) in hr_zones.items():
            if min_pct <= hr_percentage < max_pct:
                return zone_key
        return 'zone5'  # 默认最高区间
    
    def _calculate_simple_tss(self, distance_km: float, time_seconds: int) -> float:
        """计算简化的训练压力分数"""
        if distance_km <= 0 or time_seconds <= 0:
            return 0
        
        # 简化公式：基于距离和时间强度
        base_tss = distance_km * 10  # 每公里基础10分
        time_factor = time_seconds / 3600  # 时间因子
        
        return base_tss * time_factor
    
    def _calculate_pace_summary(self, pace_data: List[Dict]) -> Dict:
        """计算配速汇总统计"""
        if not pace_data:
            return {}
        
        paces = [p['pace_seconds'] for p in pace_data]
        
        return {
            'total_activities': len(pace_data),
            'average_pace_seconds': statistics.mean(paces),
            'fastest_pace_seconds': min(paces),
            'slowest_pace_seconds': max(paces),
            'pace_std_dev': statistics.stdev(paces) if len(paces) > 1 else 0,
            'average_pace_formatted': self.type_manager.format_time(int(statistics.mean(paces))),
            'fastest_pace_formatted': self.type_manager.format_time(int(min(paces))),
            'slowest_pace_formatted': self.type_manager.format_time(int(max(paces)))
        }
    
    def _generate_pace_insights(self, pace_data: List[Dict], monthly_trends: Dict) -> List[str]:
        """生成配速洞察"""
        insights = []
        
        if not pace_data:
            return insights
        
        # 配速一致性分析
        paces = [p['pace_seconds'] for p in pace_data]
        if len(paces) > 1:
            cv = statistics.stdev(paces) / statistics.mean(paces)
            if cv < 0.1:
                insights.append("🎯 配速非常稳定，一致性表现优秀")
            elif cv < 0.2:
                insights.append("✅ 配速较为稳定，保持良好")
            else:
                insights.append("⚠️ 配速波动较大，建议加强节奏训练")
        
        # 趋势分析
        if len(monthly_trends) >= 2:
            recent_months = sorted(monthly_trends.keys())[-3:]
            improvements = [monthly_trends[m]['improvement'] for m in recent_months if monthly_trends[m]['improvement'] != 0]
            
            if improvements and statistics.mean(improvements) > 5:
                insights.append("📈 近期配速有明显改善，训练效果显著")
            elif improvements and statistics.mean(improvements) < -5:
                insights.append("📉 近期配速有所下降，建议调整训练计划")
        
        return insights
    
    def _generate_hr_insights(self, zone_stats: Dict, monthly_trends: Dict) -> List[str]:
        """生成心率洞察"""
        insights = []
        
        # 心率分布分析
        total_activities = sum(zone['count'] for zone in zone_stats.values())
        if total_activities > 0:
            zone2_3_pct = (zone_stats['zone2']['count'] + zone_stats['zone3']['count']) / total_activities * 100
            if zone2_3_pct > 70:
                insights.append("💚 大部分训练在有氧区间，基础耐力训练充分")
            
            zone4_5_pct = (zone_stats['zone4']['count'] + zone_stats['zone5']['count']) / total_activities * 100
            if zone4_5_pct > 30:
                insights.append("🔥 高强度训练比例较高，注意平衡与恢复")
        
        return insights
    
    def _analyze_load_trends(self, weekly_load: Dict, monthly_load: Dict) -> Dict:
        """分析负荷趋势"""
        trends = {
            'weekly_trend': 'stable',
            'monthly_trend': 'stable',
            'load_balance': 'good'
        }
        
        # 周负荷趋势
        if len(weekly_load) >= 4:
            recent_weeks = sorted(weekly_load.keys())[-4:]
            distances = [weekly_load[w]['distance'] for w in recent_weeks]
            
            if len(distances) >= 2:
                if distances[-1] > distances[-2] * 1.1:
                    trends['weekly_trend'] = 'increasing'
                elif distances[-1] < distances[-2] * 0.9:
                    trends['weekly_trend'] = 'decreasing'
        
        return trends
    
    def _generate_training_recommendations(self, trends: Dict) -> List[str]:
        """生成训练建议"""
        recommendations = []
        
        if trends['weekly_trend'] == 'increasing':
            recommendations.append("📈 训练量持续增加，注意循序渐进避免过度训练")
        elif trends['weekly_trend'] == 'decreasing':
            recommendations.append("📉 训练量有所下降，可适当增加训练强度")
        
        return recommendations
    
    def _calculate_pace_improvement(self, paces: List[float], activities: List[Dict]) -> float:
        """计算配速改进幅度"""
        if len(paces) < 2:
            return 0
        
        # 按日期排序，计算首末配速差异
        sorted_activities = sorted(activities, key=lambda x: x.get('start_date_local', ''))
        first_pace = None
        last_pace = None
        
        for activity in sorted_activities:
            distance_km = float(activity.get('distance', 0)) / 1000
            time_seconds = self.type_manager._parse_time(activity.get('moving_time', '0'))
            
            if distance_km > 0 and time_seconds > 0:
                pace = time_seconds / distance_km
                if first_pace is None:
                    first_pace = pace
                last_pace = pace
        
        if first_pace and last_pace and first_pace != last_pace:
            # 配速越小越好，所以改进是负值
            return ((last_pace - first_pace) / first_pace) * 100 * -1
        
        return 0
    
    def _calculate_consistency(self, paces: List[float]) -> float:
        """计算配速一致性分数 (0-100)"""
        if len(paces) < 2:
            return 100
        
        cv = statistics.stdev(paces) / statistics.mean(paces)
        # 变异系数越小一致性越好
        consistency = max(0, 100 - (cv * 500))
        return round(consistency, 1)
    
    def _analyze_overall_performance_trends(self, activities: List[Dict]) -> Dict:
        """分析整体表现趋势"""
        trends = {
            'total_activities': len(activities),
            'trend_direction': 'stable',
            'activity_frequency': 'normal'
        }
        
        # 分析活动频率趋势
        if activities:
            dates = []
            for activity in activities:
                date = self._parse_date(activity.get('start_date_local', ''))
                if date:
                    dates.append(date)
            
            if len(dates) >= 2:
                dates.sort()
                date_range = (dates[-1] - dates[0]).days
                if date_range > 0:
                    frequency = len(dates) / (date_range / 7)  # 每周频率
                    
                    if frequency >= 4:
                        trends['activity_frequency'] = 'high'
                    elif frequency <= 1:
                        trends['activity_frequency'] = 'low'
        
        return trends 