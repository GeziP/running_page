"""
Basic Statistics Analyzer
基础统计分析，包括周期性统计、距离统计、时间统计等
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from .activity_classifier import ActivityTypeManager


class BasicStatsAnalyzer:
    """基础统计分析器"""

    def __init__(self):
        self.type_manager = ActivityTypeManager()

    def calculate_period_stats(
        self,
        activities: List[Dict],
        period_type: str = "monthly",
        activity_type: str = "all",
    ) -> Dict:
        """
        计算周期性统计数据

        Args:
            activities: 活动列表
            period_type: 周期类型 ('weekly', 'monthly', 'yearly')
            activity_type: 活动类型

        Returns:
            周期性统计数据
        """
        # 按活动类型筛选
        filtered_activities = self.type_manager.filter_by_type(
            activities, activity_type
        )

        # 按周期分组
        period_groups = self._group_by_period(filtered_activities, period_type)

        stats = {}
        for period, period_activities in period_groups.items():
            if not period_activities:
                continue

            stats[period] = self._calculate_period_summary(period_activities)

        return {
            "period_type": period_type,
            "activity_type": activity_type,
            "data": stats,
            "summary": self._calculate_overall_summary(stats),
        }

    def calculate_distance_distribution(
        self, activities: List[Dict], activity_type: str = "all"
    ) -> Dict:
        """
        计算距离分布统计

        Args:
            activities: 活动列表
            activity_type: 活动类型

        Returns:
            距离分布数据
        """
        filtered_activities = self.type_manager.filter_by_type(
            activities, activity_type
        )

        # 距离区间定义（公里）
        distance_ranges = [
            (0, 5, "0-5公里"),
            (5, 10, "5-10公里"),
            (10, 20, "10-20公里"),
            (20, 30, "20-30公里"),
            (30, 50, "30-50公里"),
            (50, float("inf"), "50公里以上"),
        ]

        distribution = {}
        for min_dist, max_dist, label in distance_ranges:
            count = 0
            total_distance = 0

            for activity in filtered_activities:
                distance_km = float(activity.get("distance", 0)) / 1000
                if min_dist <= distance_km < max_dist:
                    count += 1
                    total_distance += distance_km

            distribution[label] = {
                "count": count,
                "total_distance": round(total_distance, 2),
                "percentage": (
                    round(count / len(filtered_activities) * 100, 1)
                    if filtered_activities
                    else 0
                ),
            }

        return {
            "activity_type": activity_type,
            "total_activities": len(filtered_activities),
            "distribution": distribution,
        }

    def calculate_weekly_summary(
        self, activities: List[Dict], activity_type: str = "all"
    ) -> Dict:
        """
        计算最近周统计摘要

        Args:
            activities: 活动列表
            activity_type: 活动类型

        Returns:
            周统计摘要
        """
        # 获取最近7天的活动
        now = datetime.now()
        week_ago = now - timedelta(days=7)

        recent_activities = []
        for activity in activities:
            activity_date = self._parse_date(activity.get("start_date_local", ""))
            if activity_date and activity_date >= week_ago:
                recent_activities.append(activity)

        # 按活动类型筛选
        filtered_activities = self.type_manager.filter_by_type(
            recent_activities, activity_type
        )

        if not filtered_activities:
            return self._empty_summary("weekly", activity_type)

        return {
            "period": "weekly",
            "activity_type": activity_type,
            "start_date": week_ago.strftime("%Y-%m-%d"),
            "end_date": now.strftime("%Y-%m-%d"),
            "stats": self._calculate_period_summary(filtered_activities),
            "daily_breakdown": self._calculate_daily_breakdown(filtered_activities),
        }

    def calculate_monthly_summary(
        self, activities: List[Dict], activity_type: str = "all"
    ) -> Dict:
        """
        计算当月统计摘要

        Args:
            activities: 活动列表
            activity_type: 活动类型

        Returns:
            月统计摘要
        """
        now = datetime.now()
        month_start = now.replace(day=1)

        monthly_activities = []
        for activity in activities:
            activity_date = self._parse_date(activity.get("start_date_local", ""))
            if activity_date and activity_date >= month_start:
                monthly_activities.append(activity)

        # 按活动类型筛选
        filtered_activities = self.type_manager.filter_by_type(
            monthly_activities, activity_type
        )

        if not filtered_activities:
            return self._empty_summary("monthly", activity_type)

        return {
            "period": "monthly",
            "activity_type": activity_type,
            "month": now.strftime("%Y-%m"),
            "stats": self._calculate_period_summary(filtered_activities),
            "weekly_breakdown": self._calculate_weekly_breakdown_in_month(
                filtered_activities, month_start
            ),
        }

    def calculate_yearly_summary(
        self, activities: List[Dict], year: int = None, activity_type: str = "all"
    ) -> Dict:
        """
        计算年度统计摘要

        Args:
            activities: 活动列表
            year: 年份，默认为当前年份
            activity_type: 活动类型

        Returns:
            年度统计摘要
        """
        if year is None:
            year = datetime.now().year

        yearly_activities = []
        for activity in activities:
            activity_date = self._parse_date(activity.get("start_date_local", ""))
            if activity_date and activity_date.year == year:
                yearly_activities.append(activity)

        # 按活动类型筛选
        filtered_activities = self.type_manager.filter_by_type(
            yearly_activities, activity_type
        )

        if not filtered_activities:
            return self._empty_summary("yearly", activity_type)

        return {
            "period": "yearly",
            "activity_type": activity_type,
            "year": year,
            "stats": self._calculate_period_summary(filtered_activities),
            "monthly_breakdown": self._calculate_monthly_breakdown_in_year(
                filtered_activities, year
            ),
        }

    def get_personal_bests(
        self, activities: List[Dict], activity_type: str = "all"
    ) -> Dict:
        """
        获取个人最佳记录

        Args:
            activities: 活动列表
            activity_type: 活动类型

        Returns:
            个人最佳记录
        """
        filtered_activities = self.type_manager.filter_by_type(
            activities, activity_type
        )

        if not filtered_activities:
            return {}

        # 初始化记录
        records = {
            "longest_distance": {"distance": 0, "activity": None},
            "longest_time": {"time": 0, "activity": None},
            "fastest_pace": {"pace": float("inf"), "activity": None},
            "highest_speed": {"speed": 0, "activity": None},
        }

        for activity in filtered_activities:
            distance_km = float(activity.get("distance", 0)) / 1000
            time_seconds = self.type_manager._parse_time(
                activity.get("moving_time", "0")
            )
            speed = float(activity.get("average_speed", 0))

            # 最长距离
            if distance_km > records["longest_distance"]["distance"]:
                records["longest_distance"] = {
                    "distance": distance_km,
                    "activity": activity,
                }

            # 最长时间
            if time_seconds > records["longest_time"]["time"]:
                records["longest_time"] = {"time": time_seconds, "activity": activity}

            # 最快配速（仅跑步类活动）
            if (
                activity.get("type") in ["Run", "TrailRun"] and distance_km > 1
            ):  # 至少1公里才计算配速
                pace = time_seconds / distance_km if distance_km > 0 else float("inf")
                if pace < records["fastest_pace"]["pace"]:
                    records["fastest_pace"] = {"pace": pace, "activity": activity}

            # 最高速度
            if speed > records["highest_speed"]["speed"]:
                records["highest_speed"] = {"speed": speed, "activity": activity}

        return {"activity_type": activity_type, "records": records}

    def _group_by_period(self, activities: List[Dict], period_type: str) -> Dict:
        """按周期分组活动"""
        groups = defaultdict(list)

        for activity in activities:
            date = self._parse_date(activity.get("start_date_local", ""))
            if not date:
                continue

            if period_type == "weekly":
                # 获取该周的周一日期作为键
                monday = date - timedelta(days=date.weekday())
                key = monday.strftime("%Y-W%U")
            elif period_type == "monthly":
                key = date.strftime("%Y-%m")
            elif period_type == "yearly":
                key = str(date.year)
            else:
                continue

            groups[key].append(activity)

        return dict(groups)

    def _calculate_period_summary(self, activities: List[Dict]) -> Dict:
        """计算周期内活动汇总统计"""
        if not activities:
            return {
                "count": 0,
                "total_distance": 0,
                "total_time": 0,
                "avg_distance": 0,
                "avg_time": 0,
                "avg_pace": "0:00",
                "avg_speed": 0,
            }

        total_distance = (
            sum(float(a.get("distance", 0)) for a in activities) / 1000
        )  # 转换为公里
        total_time = sum(
            self.type_manager._parse_time(a.get("moving_time", "0")) for a in activities
        )
        count = len(activities)

        avg_distance = total_distance / count if count > 0 else 0
        avg_time = total_time / count if count > 0 else 0

        # 计算平均配速和速度
        total_speed = sum(float(a.get("average_speed", 0)) for a in activities)
        avg_speed = total_speed / count if count > 0 else 0

        avg_pace = (
            self.type_manager.format_pace(total_distance, total_time)
            if total_distance > 0
            else "0:00"
        )

        return {
            "count": count,
            "total_distance": round(total_distance, 2),
            "total_time": total_time,
            "avg_distance": round(avg_distance, 2),
            "avg_time": avg_time,
            "avg_pace": avg_pace,
            "avg_speed": round(avg_speed, 2),
        }

    def _calculate_overall_summary(self, period_stats: Dict) -> Dict:
        """计算总体摘要统计"""
        if not period_stats:
            return {}

        periods = list(period_stats.keys())

        total_activities = sum(stats["count"] for stats in period_stats.values())
        total_distance = sum(stats["total_distance"] for stats in period_stats.values())

        return {
            "total_periods": len(periods),
            "total_activities": total_activities,
            "total_distance": round(total_distance, 2),
            "avg_activities_per_period": (
                round(total_activities / len(periods), 1) if periods else 0
            ),
            "avg_distance_per_period": (
                round(total_distance / len(periods), 2) if periods else 0
            ),
        }

    def _calculate_daily_breakdown(self, activities: List[Dict]) -> Dict:
        """计算每日分解统计"""
        daily_stats = defaultdict(list)

        for activity in activities:
            date = self._parse_date(activity.get("start_date_local", ""))
            if date:
                day_key = date.strftime("%Y-%m-%d")
                daily_stats[day_key].append(activity)

        breakdown = {}
        for day, day_activities in daily_stats.items():
            breakdown[day] = self._calculate_period_summary(day_activities)

        return breakdown

    def _calculate_weekly_breakdown_in_month(
        self, activities: List[Dict], month_start: datetime
    ) -> Dict:
        """计算月内周分解统计"""
        weekly_stats = defaultdict(list)

        for activity in activities:
            date = self._parse_date(activity.get("start_date_local", ""))
            if date:
                # 计算是当月第几周
                week_num = (date.day - 1) // 7 + 1
                week_key = f"第{week_num}周"
                weekly_stats[week_key].append(activity)

        breakdown = {}
        for week, week_activities in weekly_stats.items():
            breakdown[week] = self._calculate_period_summary(week_activities)

        return breakdown

    def _calculate_monthly_breakdown_in_year(
        self, activities: List[Dict], year: int
    ) -> Dict:
        """计算年内月分解统计"""
        monthly_stats = defaultdict(list)

        for activity in activities:
            date = self._parse_date(activity.get("start_date_local", ""))
            if date and date.year == year:
                month_key = date.strftime("%m月")
                monthly_stats[month_key].append(activity)

        breakdown = {}
        for month, month_activities in monthly_stats.items():
            breakdown[month] = self._calculate_period_summary(month_activities)

        return breakdown

    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if not date_str:
            return None

        try:
            # 处理不同的日期格式
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    def _empty_summary(self, period: str, activity_type: str) -> Dict:
        """返回空的统计摘要"""
        return {
            "period": period,
            "activity_type": activity_type,
            "stats": {
                "count": 0,
                "total_distance": 0,
                "total_time": 0,
                "avg_distance": 0,
                "avg_time": 0,
                "avg_pace": "0:00",
                "avg_speed": 0,
            },
        }
