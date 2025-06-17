#!/usr/bin/env python3
import json

# 读取活动数据
with open("src/static/activities.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

print(f"总计: {len(activities)} 条记录")

# 按距离排序
sorted_by_distance = sorted(
    activities, key=lambda x: x.get("distance", 0), reverse=True
)

print("\n最长距离的10个活动:")
for i, activity in enumerate(sorted_by_distance[:10]):
    distance_km = activity.get("distance", 0) / 1000
    date = activity.get("start_date_local", "")[:10]
    location = activity.get("location_country", "Unknown")[:40]
    print(f"{i+1}. {distance_km:.1f}km - {location} ({date})")

# 距离分布统计
distance_ranges = {
    "0-5km": 0,
    "5-10km": 0,
    "10-15km": 0,
    "15-20km": 0,
    "20-30km": 0,
    "30km+": 0,
}

for activity in activities:
    distance_km = activity.get("distance", 0) / 1000
    if distance_km < 5:
        distance_ranges["0-5km"] += 1
    elif distance_km < 10:
        distance_ranges["5-10km"] += 1
    elif distance_km < 15:
        distance_ranges["10-15km"] += 1
    elif distance_km < 20:
        distance_ranges["15-20km"] += 1
    elif distance_km < 30:
        distance_ranges["20-30km"] += 1
    else:
        distance_ranges["30km+"] += 1

print("\n距离分布:")
for range_name, count in distance_ranges.items():
    percentage = count / len(activities) * 100
    print(f"{range_name}: {count} 条记录 ({percentage:.1f}%)")

# 检查超过20km的活动（可能是越野跑或马拉松）
long_runs = [a for a in activities if a.get("distance", 0) > 20000]  # 20公里以上
print(f"\n超过20km的活动: {len(long_runs)} 条")

if long_runs:
    print("详细信息:")
    for activity in long_runs:
        distance_km = activity.get("distance", 0) / 1000
        time = activity.get("moving_time", "Unknown")
        date = activity.get("start_date_local", "")[:10]
        location = activity.get("location_country", "Unknown")[:50]
        print(f"  {distance_km:.1f}km - {time} - {location} ({date})")
