#!/usr/bin/env python3
"""
修复activities.json中的活动类型信息
从GPX文件中读取正确的活动类型并更新到activities.json
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
        for track in root.findall(".//{http://www.topografix.com/GPX/1/1}trk"):
            type_elem = track.find(".//{http://www.topografix.com/GPX/1/1}type")
            if type_elem is not None and type_elem.text:
                return type_elem.text

        return None
    except Exception as e:
        print(f"读取GPX文件 {gpx_file} 时出错: {e}")
        return None


def fix_activity_types():
    """修复活动类型"""

    # 读取现有的activities.json
    activities_file = "../src/static/activities.json"
    if not os.path.exists(activities_file):
        print("❌ activities.json 文件不存在")
        return

    with open(activities_file, "r", encoding="utf-8") as f:
        activities = json.load(f)

    print(f"📊 加载了 {len(activities)} 条活动记录")

    # 构建GPX文件映射
    gpx_files = {}
    gpx_pattern = "../GPX_OUT/*.gpx"
    for gpx_file in glob.glob(gpx_pattern):
        # 从文件名提取ID（去掉.gpx扩展名）
        file_id = os.path.basename(gpx_file).replace(".gpx", "")
        gpx_files[file_id] = gpx_file

    print(f"🗂️ 找到 {len(gpx_files)} 个GPX文件")

    # 更新活动类型
    updated_count = 0
    type_mapping = {}

    for activity in activities:
        activity_id = str(activity.get("run_id", ""))

        if activity_id in gpx_files:
            gpx_type = get_gpx_activity_type(gpx_files[activity_id])
            if gpx_type and gpx_type != activity.get("type"):
                old_type = activity.get("type", "Unknown")
                activity["type"] = gpx_type
                type_mapping[old_type] = type_mapping.get(old_type, 0) + 1
                updated_count += 1

    print(f"🔄 更新了 {updated_count} 条记录的活动类型")

    # 统计更新后的活动类型分布
    type_counts = {}
    for activity in activities:
        activity_type = activity.get("type", "Unknown")
        type_counts[activity_type] = type_counts.get(activity_type, 0) + 1

    print("📋 更新后的活动类型分布：")
    for activity_type, count in sorted(type_counts.items()):
        print(f"  {activity_type}: {count} 条")

    # 保存更新后的文件
    if updated_count > 0:
        backup_file = activities_file + ".backup"
        import shutil

        shutil.copy2(activities_file, backup_file)
        print(f"💾 已备份原文件至 {backup_file}")

        with open(activities_file, "w", encoding="utf-8") as f:
            json.dump(activities, f, ensure_ascii=False, indent=2)

        print(f"✅ 已更新 {activities_file}")
    else:
        print("ℹ️ 没有需要更新的记录")


if __name__ == "__main__":
    fix_activity_types()
