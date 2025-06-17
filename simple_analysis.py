#!/usr/bin/env python3

import json
import os
from datetime import datetime
from pathlib import Path


def generate_clean_analysis():
    """使用清理后的数据重新生成分析"""

    # 读取活动数据
    with open("src/static/activities.json", "r", encoding="utf-8") as f:
        activities = json.load(f)

    # 过滤跑步活动（不包括unknown）
    running_activities = [
        a for a in activities if a.get("type") in ["running", "trail_running"]
    ]

    print(f"总活动数: {len(activities)}")
    print(f"跑步活动数: {len(running_activities)}")

    # 找到新的跑步最佳记录
    if running_activities:
        # 最长距离
        longest = max(running_activities, key=lambda x: x.get("distance", 0))
        print(f"\n跑步最长距离: {longest['distance']/1000:.1f}km")
        print(f"  ID: {longest['run_id']}")
        print(f"  类型: {longest['type']}")
        print(f"  日期: {longest['start_date_local']}")

        # 最快速度
        fastest = max(running_activities, key=lambda x: x.get("average_speed", 0))
        speed_kmh = fastest["average_speed"] * 3.6
        print(f"\n跑步最快速度: {speed_kmh:.1f}km/h")
        print(f"  ID: {fastest['run_id']}")
        print(f"  类型: {fastest['type']}")
        print(f"  距离: {fastest['distance']/1000:.1f}km")
        print(f"  日期: {fastest['start_date_local']}")

    # 生成简化的基础统计
    output_dir = Path("src/static/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 基础统计
    basic_stats = {
        "generated_at": datetime.now().isoformat(),
        "stats_by_type": {
            "running": {
                "personal_bests": {
                    "activity_type": "running",
                    "records": {
                        "longest_distance": (
                            {
                                "distance": longest["distance"] / 1000,
                                "activity": longest,
                            }
                            if running_activities
                            else None
                        ),
                        "highest_speed": (
                            {"speed": fastest["average_speed"], "activity": fastest}
                            if running_activities
                            else None
                        ),
                    },
                }
            }
        },
    }

    with open(output_dir / "basic_statistics.json", "w", encoding="utf-8") as f:
        json.dump(basic_stats, f, ensure_ascii=False, indent=2)

    # 类型统计
    type_counts = {}
    for activity in activities:
        activity_type = activity.get("type", "Unknown")
        type_counts[activity_type] = type_counts.get(activity_type, 0) + 1

    type_stats = {
        "generated_at": datetime.now().isoformat(),
        "total_activities": len(activities),
        "running_activities": len(running_activities),
        "type_statistics": type_counts,
    }

    with open(output_dir / "activity_types.json", "w", encoding="utf-8") as f:
        json.dump(type_stats, f, ensure_ascii=False, indent=2)

    print(f"\n已生成清理后的分析数据到: {output_dir}")
    print("\n类型分布:")
    for activity_type, count in sorted(type_counts.items()):
        print(f"  {activity_type}: {count}")


if __name__ == "__main__":
    generate_clean_analysis()
