"""
Pace Analyzer
配速分析模块，提供配速趋势、配速区间等分析功能
"""

from typing import List, Dict, Any
from collections import defaultdict
from .activity_classifier import ActivityTypeManager


class PaceAnalyzer:
    """配速分析器"""

    def __init__(self):
        self.type_manager = ActivityTypeManager()

    def analyze_pace_trends(
        self, activities: List[Dict], activity_type: str = "running"
    ) -> Dict:
        """
        分析配速趋势

        Args:
            activities: 活动列表
            activity_type: 活动类型

        Returns:
            配速趋势数据
        """
        # 仅分析跑步类活动的配速
        if activity_type not in ["running", "trail_running"]:
            return {}

        filtered_activities = self.type_manager.filter_by_type(
            activities, activity_type
        )

        pace_data = []
        for activity in filtered_activities:
            distance_km = float(activity.get("distance", 0)) / 1000
            time_seconds = self.type_manager._parse_time(
                activity.get("moving_time", "0")
            )

            if distance_km > 0 and time_seconds > 0:
                pace_seconds_per_km = time_seconds / distance_km
                pace_data.append(
                    {
                        "date": activity.get("start_date_local", "").split("T")[0],
                        "distance": distance_km,
                        "pace_seconds": pace_seconds_per_km,
                        "pace_formatted": self.type_manager.format_pace(
                            distance_km, time_seconds
                        ),
                        "activity_name": activity.get("name", ""),
                        "activity_id": activity.get("run_id"),
                    }
                )

        # 按日期排序
        pace_data.sort(key=lambda x: x["date"])

        return {
            "activity_type": activity_type,
            "pace_data": pace_data,
            "summary": self._calculate_pace_summary(pace_data),
        }

    def _calculate_pace_summary(self, pace_data: List[Dict]) -> Dict:
        """计算配速汇总统计"""
        if not pace_data:
            return {}

        paces = [p["pace_seconds"] for p in pace_data]

        return {
            "total_activities": len(pace_data),
            "average_pace_seconds": sum(paces) / len(paces),
            "fastest_pace_seconds": min(paces),
            "slowest_pace_seconds": max(paces),
            "average_pace_formatted": self.type_manager.format_time(
                int(sum(paces) / len(paces))
            ),
            "fastest_pace_formatted": self.type_manager.format_time(int(min(paces))),
            "slowest_pace_formatted": self.type_manager.format_time(int(max(paces))),
        }
