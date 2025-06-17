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

    # 检查用户质疑的50.7km记录
    target_id = 1616287392000

    for activity in activities:
        if activity['run_id'] == target_id:
            distance_km = activity['distance'] / 1000
            speed_ms = activity.get('average_speed', 0)
            speed_kmh = speed_ms * 3.6
            
            # 解析moving_time
            moving_time_str = activity.get('moving_time', '0:00')
            time_parts = moving_time_str.split(':')
            if len(time_parts) == 3:  # H:MM:SS
                total_minutes = int(time_parts[0]) * 60 + int(time_parts[1]) + int(time_parts[2]) / 60
            elif len(time_parts) == 2:  # MM:SS
                total_minutes = int(time_parts[0]) + int(time_parts[1]) / 60
            
            pace_min_per_km = total_minutes / distance_km if distance_km > 0 else 0
            
            print("=== 50.7km记录详细分析 ===")
            print(f"ID: {activity['run_id']}")
            print(f"当前类型: {activity['type']}")
            print(f"距离: {distance_km:.1f}km")
            print(f"时间: {moving_time_str}")
            print(f"速度: {speed_kmh:.1f}km/h")
            print(f"配速: {pace_min_per_km:.1f}分钟/公里")
            print(f"日期: {activity['start_date_local']}")
            print(f"心率: {activity.get('average_heartrate', 'N/A')}")
            
            # 分析这个记录的合理性
            print("\n=== 合理性分析 ===")
            if speed_kmh > 20:
                print("⚠️  速度超过20km/h，极可能是自行车")
            elif speed_kmh > 15:
                print("⚠️  速度超过15km/h，可能是自行车或高水平跑者")
            elif pace_min_per_km < 4:
                print("⚠️  配速快于4分钟/公里，需要仔细确认")
            elif distance_km > 42.195 and pace_min_per_km < 5:
                print("⚠️  超马距离且配速较快，可能是自行车")
            else:
                print("✅ 从速度和配速看像是跑步")
            
            break

if __name__ == "__main__":
    analyze_activities() 