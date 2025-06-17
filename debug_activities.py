#!/usr/bin/env python3
"""
分析activities.json文件的结构和内容
"""

import json
import os
from datetime import datetime

def analyze_activities():
    """分析activities.json文件"""
    
    activities_file = "src/static/activities.json"
    if not os.path.exists(activities_file):
        print(f"Error: {activities_file} not found")
        return
    
    with open(activities_file, 'r', encoding='utf-8') as f:
        activities = json.load(f)
    
    print(f"总共找到 {len(activities)} 个活动")
    print("\n分析前几个活动的结构：")
    
    for i, activity in enumerate(activities[:3]):
        print(f"\n活动 {i+1}:")
        for key, value in activity.items():
            print(f"  {key}: {value}")
    
    # 分析所有活动的类型
    types = {}
    for activity in activities:
        activity_type = activity.get('type', 'Unknown')
        types[activity_type] = types.get(activity_type, 0) + 1
    
    print(f"\n活动类型分布：")
    for type_name, count in types.items():
        print(f"  {type_name}: {count}")
    
    # 分析时间戳格式
    print(f"\n时间戳分析：")
    sample_timestamps = [activity['run_id'] for activity in activities[:5]]
    for ts in sample_timestamps:
        try:
            # 转换时间戳 (毫秒)
            dt = datetime.fromtimestamp(ts / 1000)
            print(f"  {ts} -> {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"  {ts} -> 转换失败: {e}")
    
    # 检查是否有其他可能用于匹配的字段
    print(f"\n可能用于匹配的字段：")
    if activities:
        sample = activities[0]
        print(f"  run_id (timestamp): {sample['run_id']}")
        print(f"  start_date: {sample.get('start_date', 'N/A')}")
        print(f"  start_date_local: {sample.get('start_date_local', 'N/A')}")
        print(f"  name: {sample.get('name', 'N/A')}")

if __name__ == "__main__":
    analyze_activities() 