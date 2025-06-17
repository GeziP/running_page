#!/usr/bin/env python3
"""
通过日期匹配GPX文件和活动记录，修复活动类型
"""

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import glob

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

if __name__ == "__main__":
    updates = match_activities_by_date() 