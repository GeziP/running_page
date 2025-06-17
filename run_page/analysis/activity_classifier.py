"""
Activity Type Classification System
支持跑步、越野跑、骑行等活动类型的分类和筛选
"""

from typing import List, Dict, Any
from collections import defaultdict

# 活动类型映射配置
ACTIVITY_TYPES = {
    "running": ["Run", "Treadmill", "running", "treadmill_running"],
    "trail_running": ["TrailRun", "Hike", "trail_running"],
    "cycling": ["Ride", "VirtualRide", "EBikeRide", "cycling", "biking"],
    "walking": ["Walk", "walking", "hiking"],
    "all": [
        "Run",
        "Treadmill",
        "running",
        "treadmill_running",
        "TrailRun",
        "Hike",
        "trail_running",
        "Ride",
        "VirtualRide",
        "EBikeRide",
        "cycling",
        "biking",
        "Walk",
        "walking",
        "hiking",
    ],
}

# 活动类型中文名称
ACTIVITY_TYPE_NAMES = {
    "running": "跑步",
    "trail_running": "越野跑",
    "cycling": "骑行",
    "walking": "步行",
    "all": "全部活动",
}

# 活动类型图标
ACTIVITY_TYPE_ICONS = {
    "running": "🏃‍♂️",
    "trail_running": "🥾",
    "cycling": "🚴‍♂️",
    "walking": "🚶‍♂️",
    "all": "🏃‍♂️🚴‍♂️",
}


class ActivityTypeManager:
    """活动类型管理器"""

    def __init__(self):
        self.activity_types = ACTIVITY_TYPES
        self.type_names = ACTIVITY_TYPE_NAMES
        self.type_icons = ACTIVITY_TYPE_ICONS

    def filter_by_type(
        self, activities: List[Dict], activity_type: str = "all"
    ) -> List[Dict]:
        """
        根据活动类型筛选活动

        Args:
            activities: 活动列表
            activity_type: 活动类型 ('running', 'trail_running', 'cycling', 'all')

        Returns:
            筛选后的活动列表
        """
        if activity_type == "all":
            return activities

        if activity_type not in self.activity_types:
            raise ValueError(f"不支持的活动类型: {activity_type}")

        allowed_types = self.activity_types[activity_type]
        return [
            activity for activity in activities if activity.get("type") in allowed_types
        ]

    def filter_by_multiple_types(
        self, activities: List[Dict], activity_types: List[str]
    ) -> List[Dict]:
        """
        根据多个活动类型筛选活动（用于对比模式）

        Args:
            activities: 活动列表
            activity_types: 活动类型列表

        Returns:
            筛选后的活动列表
        """
        if "all" in activity_types:
            return activities

        allowed_types = set()
        for activity_type in activity_types:
            if activity_type in self.activity_types:
                allowed_types.update(self.activity_types[activity_type])

        return [
            activity for activity in activities if activity.get("type") in allowed_types
        ]

    def group_by_type(self, activities: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按活动类型分组

        Args:
            activities: 活动列表

        Returns:
            按类型分组的活动字典
        """
        groups = defaultdict(list)

        for activity in activities:
            activity_type = activity.get("type", "Unknown")

            # 确定活动属于哪个主要类型
            main_type = "other"
            for type_key, type_values in self.activity_types.items():
                if type_key == "all":
                    continue
                if activity_type in type_values:
                    main_type = type_key
                    break

            groups[main_type].append(activity)

        return dict(groups)

    def get_type_statistics(self, activities: List[Dict]) -> Dict[str, Dict]:
        """
        获取各活动类型的统计信息

        Args:
            activities: 活动列表

        Returns:
            各类型的统计信息
        """
        stats = {}
        grouped_activities = self.group_by_type(activities)

        for activity_type, type_activities in grouped_activities.items():
            if not type_activities:
                continue

            total_distance = (
                sum(float(a.get("distance", 0)) for a in type_activities) / 1000
            )  # 转换为公里
            total_time = sum(
                self._parse_time(a.get("moving_time", "0:00:00"))
                for a in type_activities
            )
            count = len(type_activities)

            avg_distance = total_distance / count if count > 0 else 0
            avg_time = total_time / count if count > 0 else 0

            stats[activity_type] = {
                "name": self.type_names.get(activity_type, activity_type),
                "icon": self.type_icons.get(activity_type, "🏃‍♂️"),
                "count": count,
                "total_distance": round(total_distance, 2),
                "total_time": total_time,
                "avg_distance": round(avg_distance, 2),
                "avg_time": avg_time,
                "percentage": (
                    round(count / len(activities) * 100, 1) if activities else 0
                ),
            }

        return stats

    def get_available_types(self, activities: List[Dict]) -> List[str]:
        """
        获取活动数据中实际存在的活动类型

        Args:
            activities: 活动列表

        Returns:
            存在的活动类型列表
        """
        grouped = self.group_by_type(activities)
        return [t for t in grouped.keys() if grouped[t]]

    def _parse_time(self, time_str: str) -> int:
        """
        解析时间字符串为秒数

        Args:
            time_str: 时间字符串 (格式: "1:23:45" 或 "23:45")

        Returns:
            总秒数
        """
        if not time_str or time_str == "0":
            return 0

        try:
            # 处理不同的时间格式
            if isinstance(time_str, str):
                parts = time_str.split(":")
                if len(parts) == 3:  # H:M:S
                    hours, minutes, seconds = map(int, parts)
                    return hours * 3600 + minutes * 60 + seconds
                elif len(parts) == 2:  # M:S
                    minutes, seconds = map(int, parts)
                    return minutes * 60 + seconds
                elif len(parts) == 1:  # S
                    return int(parts[0])

            return 0
        except (ValueError, TypeError):
            return 0

    def format_time(self, total_seconds: int) -> str:
        """
        格式化秒数为时间字符串

        Args:
            total_seconds: 总秒数

        Returns:
            格式化的时间字符串
        """
        if total_seconds <= 0:
            return "0:00"

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

    def format_pace(self, distance_km: float, time_seconds: int) -> str:
        """
        计算并格式化配速

        Args:
            distance_km: 距离（公里）
            time_seconds: 时间（秒）

        Returns:
            配速字符串 (分:秒/公里)
        """
        if distance_km <= 0 or time_seconds <= 0:
            return "0:00"

        pace_seconds = time_seconds / distance_km
        minutes = int(pace_seconds // 60)
        seconds = int(pace_seconds % 60)

        return f"{minutes}:{seconds:02d}"


def get_running_activities(activities):
    """获取跑步类活动，排除不确定的活动"""
    return [
        activity
        for activity in activities
        if activity.get("type") in ["running", "trail_running"]
    ]


def filter_activities_by_type(activities, activity_type):
    """按类型过滤活动，排除unknown类型"""
    if activity_type == "all":
        # 'all'不包括unknown类型
        return [
            activity
            for activity in activities
            if activity.get("type") not in ["unknown"]
        ]
    elif activity_type == "running":
        return [
            activity
            for activity in activities
            if activity.get("type") in ["running", "trail_running"]
        ]
    else:
        return [
            activity for activity in activities if activity.get("type") == activity_type
        ]
