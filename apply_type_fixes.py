#!/usr/bin/env python3
"""
应用活动类型修复到activities.json
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

        # 查找第一个time元素
        for elem in root.iter():
            if "time" in elem.tag:
                time_str = elem.text
                if time_str:
                    # 移除Z并添加+00:00处理时区
                    if time_str.endswith("Z"):
                        time_str = time_str[:-1] + "+00:00"
                    try:
                        return datetime.fromisoformat(time_str)
                    except:
                        try:
                            return datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")
                        except:
                            pass
        return None
    except Exception as e:
        return None


def get_gpx_type(gpx_file):
    """从GPX文件中提取活动类型"""
    try:
        tree = ET.parse(gpx_file)
        root = tree.getroot()

        for elem in root.iter():
            if "type" in elem.tag.lower():
                activity_type = elem.text
                if activity_type:
                    return activity_type.strip()
        return None
    except Exception as e:
        return None


def apply_type_fixes():
    """应用类型修复"""

    # 备份原文件
    backup_file = "src/static/activities.json.backup"
    if not os.path.exists(backup_file):
        shutil.copy("src/static/activities.json", backup_file)
        print(f"Created backup: {backup_file}")

    # 加载活动数据
    with open("src/static/activities.json", "r", encoding="utf-8") as f:
        activities = json.load(f)

    print(f"加载了 {len(activities)} 个活动")

    # 创建GPX文件映射
    gpx_files = glob.glob("GPX_OUT/*.gpx")
    gpx_date_map = {}
    gpx_type_map = {}

    for gpx_file in gpx_files:
        gpx_date = parse_gpx_date(gpx_file)
        gpx_type = get_gpx_type(gpx_file)

        if gpx_date and gpx_type:
            date_key = gpx_date.strftime("%Y-%m-%d %H:%M:%S")
            gpx_date_map[date_key] = gpx_file
            gpx_type_map[date_key] = gpx_type

    # 应用更新
    updates_applied = 0
    type_stats = {}

    for activity in activities:
        activity_date = activity["start_date"]
        old_type = activity["type"]

        # 寻找匹配的GPX文件
        best_match = None
        min_diff = timedelta(hours=1)

        try:
            activity_dt = datetime.strptime(activity_date, "%Y-%m-%d %H:%M:%S")

            for gpx_date_str, gpx_file in gpx_date_map.items():
                gpx_dt = datetime.strptime(gpx_date_str, "%Y-%m-%d %H:%M:%S")
                diff = abs(activity_dt - gpx_dt)

                if diff < min_diff:
                    min_diff = diff
                    best_match = gpx_date_str

            # 如果找到匹配，更新类型
            if best_match and min_diff < timedelta(hours=1):
                new_type = gpx_type_map[best_match]

                if new_type != old_type:
                    activity["type"] = new_type
                    updates_applied += 1
                    print(f"更新活动 {activity['run_id']}: {old_type} -> {new_type}")

                # 统计最终类型分布
                type_stats[new_type] = type_stats.get(new_type, 0) + 1
            else:
                # 没有匹配的保持原类型
                type_stats[old_type] = type_stats.get(old_type, 0) + 1

        except Exception as e:
            print(f"Error processing activity {activity['run_id']}: {e}")
            type_stats[old_type] = type_stats.get(old_type, 0) + 1

    print(f"\n更新结果:")
    print(f"  应用了 {updates_applied} 个类型更新")
    print(f"  最终类型分布:")
    for type_name, count in type_stats.items():
        print(f"    {type_name}: {count}")

    # 保存更新后的文件
    with open("src/static/activities.json", "w", encoding="utf-8") as f:
        json.dump(activities, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\n已保存更新后的activities.json")

    # 验证更新
    with open("src/static/activities.json", "r", encoding="utf-8") as f:
        updated_activities = json.load(f)

    verify_types = {}
    for activity in updated_activities:
        activity_type = activity["type"]
        verify_types[activity_type] = verify_types.get(activity_type, 0) + 1

    print(f"\n验证结果 - 实际类型分布:")
    for type_name, count in verify_types.items():
        print(f"  {type_name}: {count}")

    return updates_applied


if __name__ == "__main__":
    updates = apply_type_fixes()
