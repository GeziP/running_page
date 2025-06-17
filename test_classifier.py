#!/usr/bin/env python3
import json
import sys

sys.path.append(".")
from run_page.analysis.activity_classifier import ActivityTypeManager

# 读取活动数据
with open("src/static/activities.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

print(f"总活动数: {len(activities)}")

# 测试分类器
manager = ActivityTypeManager()

# 检查分组结果
grouped = manager.group_by_type(activities)
print(f"\n分类器分组结果:")
for group_type, group_activities in grouped.items():
    print(f"  {group_type}: {len(group_activities)} 条活动")

# 检查可用类型
available_types = manager.get_available_types(activities)
print(f"\n可用类型: {available_types}")

# 检查统计信息
stats = manager.get_type_statistics(activities)
print(f"\n统计信息:")
for stat_type, stat_data in stats.items():
    print(f"  {stat_type}: {stat_data['name']} - {stat_data['count']} 条记录")

# 检查原始数据中的具体类型
print(f"\n原始数据类型分布:")
raw_types = {}
for activity in activities:
    activity_type = activity.get("type", "Unknown")
    raw_types[activity_type] = raw_types.get(activity_type, 0) + 1

for raw_type, count in sorted(raw_types.items()):
    print(f"  {raw_type}: {count} 条记录")

# 测试每种类型的匹配
print(f"\n类型匹配测试:")
test_types = ["running", "trail_running", "Run"]
for test_type in test_types:
    matches = 0
    for type_key, type_values in manager.activity_types.items():
        if type_key == "all":
            continue
        if test_type in type_values:
            matches += 1
            print(f"  {test_type} -> 匹配到分类: {type_key}")
    if matches == 0:
        print(f"  {test_type} -> 未匹配到任何分类")
