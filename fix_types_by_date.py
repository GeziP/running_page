#!/usr/bin/env python3
"""
通过日期匹配GPX文件和活动记录，修复活动类型
"""

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import glob
import shutil

def parse_gpx_date(gpx_file):
    """从GPX文件中提取开始时间"""
    try:
        tree = ET.parse(gpx_file)
        root = tree.getroot()
        
        # 查找第一个trkpt或第一个time元素
        for trkpt in root.iter():
            if 'time' in trkpt.tag:
                time_str = trkpt.text
                # 解析ISO 8601格式的时间
                if time_str:
                    # 移除Z并添加+00:00处理时区
                    if time_str.endswith('Z'):
                        time_str = time_str[:-1] + '+00:00'
                    try:
                        return datetime.fromisoformat(time_str)
                    except:
                        # 尝试其他格式
                        try:
                            return datetime.strptime(time_str[:19], '%Y-%m-%dT%H:%M:%S')
                        except:
                            pass
        return None
    except Exception as e:
        print(f"Error parsing {gpx_file}: {e}")
        return None

def get_gpx_type(gpx_file):
    """从GPX文件中提取活动类型"""
    try:
        tree = ET.parse(gpx_file)
        root = tree.getroot()
        
        # 查找type元素
        for elem in root.iter():
            if 'type' in elem.tag.lower():
                activity_type = elem.text
                if activity_type:
                    return activity_type.strip()
        return None
    except Exception as e:
        print(f"Error getting type from {gpx_file}: {e}")
        return None

def match_activities_by_date():
    """通过日期匹配活动和GPX文件"""
    
    # 加载活动数据
    with open("src/static/activities.json", 'r', encoding='utf-8') as f:
        activities = json.load(f)
    
    print(f"加载了 {len(activities)} 个活动")
    
    # 查找所有GPX文件
    gpx_files = glob.glob("GPX_OUT/*.gpx")
    print(f"找到 {len(gpx_files)} 个GPX文件")
    
    # 创建GPX文件的日期索引
    gpx_date_map = {}
    gpx_type_map = {}
    
    for gpx_file in gpx_files:
        gpx_date = parse_gpx_date(gpx_file)
        gpx_type = get_gpx_type(gpx_file)
        
        if gpx_date and gpx_type:
            # 使用日期字符串作为键
            date_key = gpx_date.strftime('%Y-%m-%d %H:%M:%S')
            gpx_date_map[date_key] = gpx_file
            gpx_type_map[date_key] = gpx_type
    
    print(f"成功解析了 {len(gpx_date_map)} 个GPX文件的日期和类型")
    
    # 匹配活动
    matches = 0
    type_updates = {}
    
    for activity in activities:
        activity_date = activity['start_date']  # 格式: "2018-04-20 09:46:59"
        
        # 寻找匹配的GPX文件 (允许一定的时间差)
        best_match = None
        min_diff = timedelta(hours=24)  # 最大允许24小时差异
        
        try:
            activity_dt = datetime.strptime(activity_date, '%Y-%m-%d %H:%M:%S')
            
            for gpx_date_str, gpx_file in gpx_date_map.items():
                gpx_dt = datetime.strptime(gpx_date_str, '%Y-%m-%d %H:%M:%S')
                diff = abs(activity_dt - gpx_dt)
                
                if diff < min_diff:
                    min_diff = diff
                    best_match = gpx_date_str
            
            # 如果找到了较好的匹配 (时间差小于1小时)
            if best_match and min_diff < timedelta(hours=1):
                gpx_type = gpx_type_map[best_match]
                current_type = activity['type']
                
                if gpx_type != current_type:
                    type_updates[activity['run_id']] = {
                        'old_type': current_type,
                        'new_type': gpx_type,
                        'date': activity_date,
                        'gpx_file': gpx_date_map[best_match],
                        'time_diff': str(min_diff)
                    }
                
                matches += 1
        
        except Exception as e:
            print(f"Error processing activity {activity['run_id']}: {e}")
    
    print(f"\n匹配结果:")
    print(f"  成功匹配: {matches}/{len(activities)}")
    print(f"  需要更新类型: {len(type_updates)}")
    
    if type_updates:
        print(f"\n需要更新的活动类型:")
        type_counts = {}
        for update in type_updates.values():
            new_type = update['new_type']
            type_counts[new_type] = type_counts.get(new_type, 0) + 1
        
        for type_name, count in type_counts.items():
            print(f"  {type_name}: {count} 个活动")
        
        # 显示一些示例
        print(f"\n示例更新 (前5个):")
        for i, (run_id, update) in enumerate(list(type_updates.items())[:5]):
            print(f"  ID {run_id}: {update['old_type']} -> {update['new_type']}")
            print(f"    日期: {update['date']}, 时间差: {update['time_diff']}")
    
    return type_updates

def is_likely_cycling(distance_km, speed_kmh, pace_min_per_km, duration_hours):
    """更智能的自行车判断逻辑"""
    
    # 极明显的自行车特征
    if speed_kmh > 30:  # 极高速度
        return True, "速度过高(>30km/h)"
    
    if distance_km > 80:  # 极长距离
        return True, "距离过长(>80km)"
    
    # 综合判断：长距离 + 快速度的组合
    if distance_km > 50 and speed_kmh > 18:
        return True, f"长距离({distance_km:.1f}km) + 高速({speed_kmh:.1f}km/h)"
    
    if distance_km > 40 and pace_min_per_km < 3.5:
        return True, f"长距离({distance_km:.1f}km) + 快配速({pace_min_per_km:.1f}min/km)"
    
    # 持续高速
    if speed_kmh > 25:
        return True, f"持续高速({speed_kmh:.1f}km/h)"
    
    # 超长时间 + 高速
    if duration_hours > 3 and speed_kmh > 20:
        return True, f"长时间({duration_hours:.1f}h) + 高速({speed_kmh:.1f}km/h)"
    
    return False, "符合跑步特征"

def analyze_unmatched_activities():
    """分析未匹配的活动"""
    
    # 读取activities.json
    with open('src/static/activities.json', 'r', encoding='utf-8') as f:
        activities = json.load(f)
    
    # 创建备份
    shutil.copy('src/static/activities.json', 'src/static/activities.json.backup3')
    
    print("=== 分析未匹配的'Run'类型活动 ===")
    
    run_activities = [a for a in activities if a.get('type') == 'Run']
    print(f"找到 {len(run_activities)} 个未匹配的'Run'活动")
    
    cycling_candidates = []
    keep_as_unknown = []
    
    for activity in run_activities:
        distance_km = activity['distance'] / 1000
        speed_ms = activity.get('average_speed', 0)
        speed_kmh = speed_ms * 3.6
        
        # 解析时间
        moving_time_str = activity.get('moving_time', '0:00')
        time_parts = moving_time_str.split(':')
        if len(time_parts) == 3:  # H:MM:SS
            duration_hours = int(time_parts[0]) + int(time_parts[1])/60 + int(time_parts[2])/3600
            total_minutes = int(time_parts[0]) * 60 + int(time_parts[1]) + int(time_parts[2]) / 60
        elif len(time_parts) == 2:  # MM:SS
            duration_hours = int(time_parts[0])/60 + int(time_parts[1])/3600
            total_minutes = int(time_parts[0]) + int(time_parts[1]) / 60
        else:
            duration_hours = 0
            total_minutes = 0
        
        pace_min_per_km = total_minutes / distance_km if distance_km > 0 else 999
        
        is_cycling, reason = is_likely_cycling(distance_km, speed_kmh, pace_min_per_km, duration_hours)
        
        activity_info = {
            'activity': activity,
            'distance_km': distance_km,
            'speed_kmh': speed_kmh,
            'pace_min_per_km': pace_min_per_km,
            'duration_hours': duration_hours,
            'is_cycling': is_cycling,
            'reason': reason
        }
        
        if is_cycling:
            cycling_candidates.append(activity_info)
        else:
            keep_as_unknown.append(activity_info)
    
    print(f"\n发现 {len(cycling_candidates)} 个可能的自行车活动：")
    for i, info in enumerate(cycling_candidates):
        act = info['activity']
        print(f"{i+1}. ID: {act['run_id']}")
        print(f"   距离: {info['distance_km']:.1f}km")
        print(f"   速度: {info['speed_kmh']:.1f}km/h")
        print(f"   配速: {info['pace_min_per_km']:.1f}分钟/公里")
        print(f"   时长: {info['duration_hours']:.1f}小时")
        print(f"   日期: {act['start_date_local']}")
        print(f"   判断原因: {info['reason']}")
        print()
    
    print(f"保持为未知类型的活动: {len(keep_as_unknown)} 个")
    
    # 询问用户确认
    print("\n=== 建议的修改 ===")
    print(f"1. 将 {len(cycling_candidates)} 个活动标记为 'cycling'")
    print(f"2. 将 {len(keep_as_unknown)} 个活动标记为 'unknown'（不参与跑步统计）")
    
    return cycling_candidates, keep_as_unknown

def apply_conservative_fixes():
    """应用保守的类型修正"""
    
    cycling_candidates, unknown_candidates = analyze_unmatched_activities()
    
    # 读取activities.json
    with open('src/static/activities.json', 'r', encoding='utf-8') as f:
        activities = json.load(f)
    
    # 应用修改
    cycling_ids = [c['activity']['run_id'] for c in cycling_candidates]
    unknown_ids = [u['activity']['run_id'] for u in unknown_candidates]
    
    for activity in activities:
        if activity['run_id'] in cycling_ids:
            activity['type'] = 'cycling'
        elif activity['run_id'] in unknown_ids:
            activity['type'] = 'unknown'  # 不参与跑步统计
    
    # 保存
    with open('src/static/activities.json', 'w', encoding='utf-8') as f:
        json.dump(activities, f, ensure_ascii=False, indent=2)
    
    # 统计结果
    type_counts = {}
    for activity in activities:
        activity_type = activity.get('type', 'Unknown')
        type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
    
    print("\n=== 修正完成 ===")
    print(f"修正了 {len(cycling_candidates)} 个活动为cycling")
    print(f"标记了 {len(unknown_candidates)} 个活动为unknown")
    print("\n最终类型分布:")
    for activity_type, count in sorted(type_counts.items()):
        print(f"  {activity_type}: {count}")

if __name__ == "__main__":
    apply_conservative_fixes() 