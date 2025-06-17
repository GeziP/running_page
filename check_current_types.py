#!/usr/bin/env python3
import json

# 读取当前活动数据
with open("src/static/activities.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

print(f"总活动数: {len(activities)}")

# 统计类型分布
type_counts = {}
for activity in activities:
    activity_type = activity.get("type", "Unknown")
    type_counts[activity_type] = type_counts.get(activity_type, 0) + 1

print("\n当前activities.json中的类型分布:")
for activity_type, count in sorted(type_counts.items()):
    print(f"  {activity_type}: {count} 条记录")

# 显示每种类型的几个示例
print("\n各类型示例:")
type_samples = {}
for activity in activities:
    activity_type = activity.get("type", "Unknown")
    if activity_type not in type_samples:
        type_samples[activity_type] = []
    if len(type_samples[activity_type]) < 3:
        type_samples[activity_type].append(
            {
                "id": activity.get("run_id"),
                "date": activity.get("start_date_local", "")[:10],
                "distance": activity.get("distance", 0) / 1000,
            }
        )

for activity_type, samples in type_samples.items():
    print(f"\n{activity_type} 示例:")
    for sample in samples:
        print(
            f"  ID: {sample['id']}, 日期: {sample['date']}, 距离: {sample['distance']:.1f}km"
        )
