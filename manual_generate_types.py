#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(".")
from run_page.analysis.activity_classifier import ActivityTypeManager

# 读取活动数据
with open("src/static/activities.json", "r", encoding="utf-8") as f:
    activities = json.load(f)

print(f"总活动数: {len(activities)}")

# 手动生成活动类型统计
type_manager = ActivityTypeManager()
type_stats = type_manager.get_type_statistics(activities)
available_types = type_manager.get_available_types(activities)

print(f"可用类型: {available_types}")
print(f"统计信息: {type_stats}")

# 构建输出数据
output_data = {
    "generated_at": datetime.now().isoformat(),
    "total_activities": len(activities),
    "available_types": available_types,
    "type_statistics": type_stats,
}

# 确保输出目录存在
src_output_dir = Path("src/static/analysis")
src_output_dir.mkdir(parents=True, exist_ok=True)

public_output_dir = Path("public/static/analysis")
public_output_dir.mkdir(parents=True, exist_ok=True)

# 写入文件
output_dirs = [src_output_dir, public_output_dir]
for output_dir in output_dirs:
    output_file = output_dir / "activity_types.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存到: {output_file}")

print(f"\n生成的数据:")
print(json.dumps(output_data, ensure_ascii=False, indent=2))
