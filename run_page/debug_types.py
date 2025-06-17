#!/usr/bin/env python3
"""
调试活动类型问题
"""

import json
import os
import glob
import xml.etree.ElementTree as ET

def get_gpx_activity_type(gpx_file):
    """从GPX文件中提取活动类型"""
    try:
        tree = ET.parse(gpx_file)
        root = tree.getroot()
        
        # 查找所有track元素
        for track in root.findall('.//{http://www.topografix.com/GPX/1/1}trk'):
            type_elem = track.find('.//{http://www.topografix.com/GPX/1/1}type')
            if type_elem is not None and type_elem.text:
                return type_elem.text
        
        return None
    except Exception as e:
        print(f"读取GPX文件 {gpx_file} 时出错: {e}")
        return None

def debug_types():
    """调试类型信息"""
    
    # 读取现有的activities.json
    activities_file = '../src/static/activities.json'
    with open(activities_file, 'r', encoding='utf-8') as f:
        activities = json.load(f)
    
    print(f"📊 加载了 {len(activities)} 条活动记录")
    
    # 检查前几条记录
    print("\n🔍 检查前5条活动记录：")
    for i, activity in enumerate(activities[:5]):
        activity_id = str(activity.get('run_id', ''))
        activity_type = activity.get('type', 'Unknown')
        print(f"  {i+1}. ID: {activity_id}, 当前类型: {activity_type}")
        
        # 查找对应的GPX文件
        gpx_file = f'../GPX_OUT/{activity_id}.gpx'
        if os.path.exists(gpx_file):
            gpx_type = get_gpx_activity_type(gpx_file)
            print(f"     GPX文件类型: {gpx_type}")
            if gpx_type != activity_type:
                print(f"     ⚠️ 类型不匹配！ {activity_type} -> {gpx_type}")
        else:
            print(f"     ❌ GPX文件不存在: {gpx_file}")
    
    # 统计GPX文件中的类型分布
    print("\n📋 GPX文件中的类型分布：")
    gpx_types = {}
    gpx_pattern = '../GPX_OUT/*.gpx'
    
    for gpx_file in glob.glob(gpx_pattern)[:50]:  # 只检查前50个
        gpx_type = get_gpx_activity_type(gpx_file)
        if gpx_type:
            gpx_types[gpx_type] = gpx_types.get(gpx_type, 0) + 1
    
    for gpx_type, count in sorted(gpx_types.items()):
        print(f"  {gpx_type}: {count} 个文件")

if __name__ == "__main__":
    debug_types() 