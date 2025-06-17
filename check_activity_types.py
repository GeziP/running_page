#!/usr/bin/env python3
"""检查活动类型分布"""

import sys

sys.path.append(".")
from run_page.generator.db import Activities


def main():
    # 加载活动数据
    activities_db = Activities("data.db")
    runs = activities_db.get_all_runs()

    # 统计各种类型
    type_counts = {}
    name_samples = {}  # 记录每种类型的名称样本

    for run in runs:
        run_type = getattr(run, "type", "Unknown")
        run_name = getattr(run, "name", "Unnamed")

        type_counts[run_type] = type_counts.get(run_type, 0) + 1

        # 记录每种类型的名称样本（最多5个）
        if run_type not in name_samples:
            name_samples[run_type] = []
        if len(name_samples[run_type]) < 5:
            name_samples[run_type].append(run_name)

    print("活动类型统计：")
    print("=" * 50)
    for type_name, count in sorted(type_counts.items()):
        print(f"{type_name}: {count} 条记录")
        print(f"  名称样本: {name_samples[type_name][:3]}")
        print()

    print(f"总计: {len(runs)} 条记录")


if __name__ == "__main__":
    main()
