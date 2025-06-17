#!/usr/bin/env python3

import json
from datetime import datetime

with open("src/static/activities.json", 'r', encoding='utf-8') as f:
    activities = json.load(f)

print(f"Total activities: {len(activities)}")

# 分析活动类型
types = {}
for activity in activities:
    activity_type = activity.get('type', 'Unknown')
    types[activity_type] = types.get(activity_type, 0) + 1

print("Activity types:")
for type_name, count in types.items():
    print(f"  {type_name}: {count}")

# 检查时间戳格式
sample = activities[0]
ts = sample['run_id']
dt = datetime.fromtimestamp(ts / 1000)
print(f"\nTimestamp format: {ts} -> {dt.strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\nSample fields:")
print(f"  run_id: {sample['run_id']}")
print(f"  start_date: {sample['start_date']}")
print(f"  name: {sample['name']}") 