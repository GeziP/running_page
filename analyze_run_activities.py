#!/usr/bin/env python3
"""
分析活动数据，找出长距离和高速度的活动，并寻找规律。
"""

import json
import os
import xml.etree.ElementTree as ET

def get_gpx_type(run_id):
    """从对应的GPX文件中获取原始类型"""
    gpx_file_path = f"GPX_OUT/{run_id}.gpx"
    if not os.path.exists(gpx_file_path):
        return None
    try:
        tree = ET.parse(gpx_file_path)
        root = tree.getroot()
        type_elem = root.find(".//{http://www.topografix.com/GPX/1/1}type")
        if type_elem is not None and type_elem.text:
            return type_elem.text.strip()
        return "No Type Tag"
    except Exception:
        return "Parse Error"

def analyze_extreme_activities():
    """分析超长距离和超高速度的活动"""
    try:
        with open("src/static/activities.json", "r", encoding="utf-8") as f:
            activities = json.load(f)
    except FileNotFoundError:
        print("错误：src/static/activities.json 文件未找到。")
        return

    long_distance_activities = []
    high_speed_activities = []

    for activity in activities:
        distance_km = activity.get("distance", 0) / 1000
        
        # 速度计算
        moving_time_seconds = 0
        moving_time_str = activity.get("moving_time", "0:0:0")
        parts = list(map(int, moving_time_str.split(':')))
        if len(parts) == 3:
            moving_time_seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            moving_time_seconds = parts[0] * 60 + parts[1]
        
        speed_kmh = (distance_km / moving_time_seconds * 3600) if moving_time_seconds > 0 else 0

        # 筛选活动
        if distance_km > 50:
            long_distance_activities.append((activity, distance_km, speed_kmh))
        
        if speed_kmh > 20:
            high_speed_activities.append((activity, distance_km, speed_kmh))

    print("="*20)
    print("🚴‍ 可能的自行车活动分析 🚴‍")
    print("="*20)

    print(f"\n[1] 距离超过 50 公里的活动 ({len(long_distance_activities)} 条):")
    if not long_distance_activities:
        print("  无")
    else:
        for activity, dist, speed in long_distance_activities:
            run_id = activity.get("run_id")
            original_gpx_type = get_gpx_type(run_id)
            print(f"  - ID: {run_id}")
            print(f"    日期: {activity.get('start_date_local', '')[:10]}")
            print(f"    距离: {dist:.2f} km")
            print(f"    速度: {speed:.2f} km/h")
            print(f"    当前类型 (activities.json): {activity.get('type')}")
            print(f"    原始类型 (GPX file): {original_gpx_type}")
    
    print(f"\n[2] 平均速度超过 20 km/h 的活动 ({len(high_speed_activities)} 条):")
    if not high_speed_activities:
        print("  无")
    else:
        for activity, dist, speed in high_speed_activities:
            run_id = activity.get("run_id")
            original_gpx_type = get_gpx_type(run_id)
            print(f"  - ID: {run_id}")
            print(f"    日期: {activity.get('start_date_local', '')[:10]}")
            print(f"    距离: {dist:.2f} km")
            print(f"    速度: {speed:.2f} km/h")
            print(f"    当前类型 (activities.json): {activity.get('type')}")
            print(f"    原始类型 (GPX file): {original_gpx_type}")

if __name__ == "__main__":
    analyze_extreme_activities() 