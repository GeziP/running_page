#!/usr/bin/env python3
import json

# 读取活动数据
with open("src/static/activities.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

# 统计原始类型
original_types = {}
for activity in activities:
    activity_type = activity.get("type", "Unknown")
    original_types[activity_type] = original_types.get(activity_type, 0) + 1

print("原始活动类型分布:")
for type_name, count in sorted(original_types.items()):
    print(f"  {type_name}: {count} 条记录")

print(f"\n总计: {len(activities)} 条记录")

# 查看前10个活动的详情
print("\n前10个活动的详情:")
for i, activity in enumerate(activities[:10]):
    distance_km = activity.get("distance", 0) / 1000
    print(f"{i+1}. ID: {activity.get('run_id')}")
    print(f"   Type: {activity.get('type')}")
    print(f"   Name: {activity.get('name')}")
    print(f"   Distance: {distance_km:.1f}km")
    print(f"   Time: {activity.get('moving_time')}")
    print(f"   Date: {activity.get('start_date_local')}")
    print(f"   Location: {activity.get('location_country', 'Unknown')[:50]}")
    print()

# 找出最长距离的活动（可能是越野跑）
print("最长距离的10个活动：")
sorted_by_distance = sorted(
    activities, key=lambda x: x.get("distance", 0), reverse=True
)
for i, activity in enumerate(sorted_by_distance[:10]):
    distance_km = activity.get("distance", 0) / 1000
    print(
        f"{i+1}. {distance_km:.1f}km - {activity.get('name')} ({activity.get('start_date_local', '')[:10]})"
    )

# 查看活动名称中是否有特殊关键词
print("\n查找可能的越野跑关键词:")
trail_keywords = ["trail", "hike", "hiking", "越野", "徒步", "爬山", "山地"]
potential_trail_runs = []

for activity in activities:
    name = activity.get("name", "").lower()
    location = activity.get("location_country", "").lower()

    for keyword in trail_keywords:
        if keyword in name or keyword in location:
            potential_trail_runs.append(activity)
            break

print(f"可能的越野跑活动: {len(potential_trail_runs)} 条")
for activity in potential_trail_runs[:5]:  # 只显示前5个
    distance_km = activity.get("distance", 0) / 1000
    print(
        f"  - {distance_km:.1f}km - {activity.get('name')} ({activity.get('start_date_local', '')[:10]})"
    )

# 读取分析后的活动类型统计
try:
    with open("src/static/analysis/activity_types.json", "r", encoding="utf-8") as f:
        activity_types_data = json.load(f)

    print("\n分析后的活动类型分布:")
    for type_name, stats in activity_types_data.get("type_statistics", {}).items():
        print(f"  {stats.get('name', type_name)}: {stats.get('count', 0)} 条记录")
except Exception as e:
    print(f"\n无法读取分析后的活动类型数据: {e}")
