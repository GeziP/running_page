#!/usr/bin/env python3
import json
import sys

sys.path.append(".")
from run_page.analysis.activity_classifier import ActivityTypeManager

# 读取活动数据
with open("src/static/activities.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

print(f"总活动数: {len(activities)}")

manager = ActivityTypeManager()

# 调试get_available_types方法
print(f"\n调试get_available_types方法:")
grouped = manager.group_by_type(activities)
print(f"分组结果: {list(grouped.keys())}")

available_types = manager.get_available_types(activities)
print(f"可用类型: {available_types}")

# 手动检查get_available_types的逻辑
print(f"\n手动检查逻辑:")
grouped_manual = manager.group_by_type(activities)
manual_available = [t for t in grouped_manual.keys() if grouped_manual[t]]
print(f"手动计算的可用类型: {manual_available}")

# 检查每个分组是否为空
print(f"\n检查每个分组:")
for group_type, group_activities in grouped.items():
    print(f"  {group_type}: {len(group_activities)} 条活动")
    print(f"    是否为空: {not bool(group_activities)}")
    print(f"    布尔值: {bool(group_activities)}")

# 生成完整的统计信息
print(f"\n完整统计信息:")
stats = manager.get_type_statistics(activities)
for stat_type, stat_data in stats.items():
    print(f"  {stat_type}: {stat_data}")
