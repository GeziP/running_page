#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
运动数据分析生成器
生成各种统计分析数据，支持按活动类型分类
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator import Generator
from analysis import ActivityTypeManager, BasicStatsAnalyzer, AdvancedStatsAnalyzer
from config import SQL_FILE


def load_activities_from_db():
    """从数据库加载活动数据"""
    try:
        generator = Generator(SQL_FILE)
        activities_list = generator.load()
        print(f"✅ 成功加载 {len(activities_list)} 条活动记录")
        return activities_list
    except Exception as e:
        print(f"❌ 加载活动数据失败: {e}")
        return []


def ensure_output_dir():
    """确保输出目录存在"""
    output_dir = Path("src/static/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_activity_types(activities, output_dir):
    """生成活动类型统计"""
    print("📊 生成活动类型统计...")

    type_manager = ActivityTypeManager()
    type_stats = type_manager.get_type_statistics(activities)

    # 获取可用的活动类型
    available_types = type_manager.get_available_types(activities)

    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_activities": len(activities),
        "available_types": available_types,
        "type_statistics": type_stats,
    }

    output_file = output_dir / "activity_types.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 活动类型统计已保存到: {output_file}")
    return type_stats


def generate_basic_statistics(activities, output_dir):
    """生成基础统计分析"""
    print("📈 生成基础统计分析...")

    type_manager = ActivityTypeManager()
    stats_analyzer = BasicStatsAnalyzer()

    # 获取可用的活动类型
    available_types = ["all"] + type_manager.get_available_types(activities)

    all_stats = {}

    for activity_type in available_types:
        print(
            f"  处理活动类型: {type_manager.type_names.get(activity_type, activity_type)}"
        )

        # 周期性统计
        weekly_stats = stats_analyzer.calculate_period_stats(
            activities, "weekly", activity_type
        )
        monthly_stats = stats_analyzer.calculate_period_stats(
            activities, "monthly", activity_type
        )
        yearly_stats = stats_analyzer.calculate_period_stats(
            activities, "yearly", activity_type
        )

        # 距离分布
        distance_dist = stats_analyzer.calculate_distance_distribution(
            activities, activity_type
        )

        # 个人最佳记录
        personal_bests = stats_analyzer.get_personal_bests(activities, activity_type)

        all_stats[activity_type] = {
            "weekly": weekly_stats,
            "monthly": monthly_stats,
            "yearly": yearly_stats,
            "distance_distribution": distance_dist,
            "personal_bests": personal_bests,
        }

    output_data = {
        "generated_at": datetime.now().isoformat(),
        "stats_by_type": all_stats,
    }

    output_file = output_dir / "basic_statistics.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 基础统计分析已保存到: {output_file}")
    return all_stats


def generate_advanced_analysis(activities, output_dir):
    """生成高级分析数据"""
    print("🔬 生成高级分析数据...")

    type_manager = ActivityTypeManager()
    advanced_analyzer = AdvancedStatsAnalyzer()

    # 获取可用的活动类型
    available_types = ["all"] + type_manager.get_available_types(activities)

    advanced_stats = {}

    for activity_type in available_types:
        if activity_type in ["running", "trail_running", "all"]:
            print(
                f"  分析活动类型: {type_manager.type_names.get(activity_type, activity_type)}"
            )

            # 配速趋势分析
            pace_trends = advanced_analyzer.analyze_pace_trends(
                activities, activity_type
            )

            advanced_stats[activity_type] = {"pace_trends": pace_trends}

    output_data = {
        "generated_at": datetime.now().isoformat(),
        "advanced_stats_by_type": advanced_stats,
    }

    output_file = output_dir / "advanced_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 高级分析数据已保存到: {output_file}")
    return advanced_stats


def generate_recent_summary(activities, output_dir):
    """生成最近活动摘要"""
    print("📅 生成最近活动摘要...")

    stats_analyzer = BasicStatsAnalyzer()
    type_manager = ActivityTypeManager()

    available_types = ["all"] + type_manager.get_available_types(activities)

    summaries = {}

    for activity_type in available_types:
        # 最近7天
        weekly_summary = stats_analyzer.calculate_period_stats(
            activities, "weekly", activity_type
        )

        # 当月
        monthly_summary = stats_analyzer.calculate_period_stats(
            activities, "monthly", activity_type
        )

        # 当年
        yearly_summary = stats_analyzer.calculate_period_stats(
            activities, "yearly", activity_type
        )

        summaries[activity_type] = {
            "weekly": weekly_summary,
            "monthly": monthly_summary,
            "yearly": yearly_summary,
        }

    output_data = {
        "generated_at": datetime.now().isoformat(),
        "recent_summaries": summaries,
    }

    output_file = output_dir / "recent_summary.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 最近活动摘要已保存到: {output_file}")
    return summaries


def generate_analysis_overview(activities, output_dir):
    """生成分析概览"""
    print("🔍 生成分析概览...")

    type_manager = ActivityTypeManager()

    # 基本信息
    total_activities = len(activities)
    available_types = type_manager.get_available_types(activities)
    type_stats = type_manager.get_type_statistics(activities)

    # 时间范围
    dates = []
    for activity in activities:
        date_str = activity.get("start_date_local", "")
        if date_str:
            try:
                if "T" in date_str:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date)
            except:
                continue

    date_range = {}
    if dates:
        dates.sort()
        date_range = {
            "earliest": dates[0].strftime("%Y-%m-%d"),
            "latest": dates[-1].strftime("%Y-%m-%d"),
            "total_days": (dates[-1] - dates[0]).days + 1,
        }

    # 总体统计
    total_distance = sum(float(a.get("distance", 0)) for a in activities) / 1000
    total_time = sum(
        type_manager._parse_time(a.get("moving_time", "0")) for a in activities
    )

    overview = {
        "generated_at": datetime.now().isoformat(),
        "overview": {
            "total_activities": total_activities,
            "available_types": available_types,
            "total_distance_km": round(total_distance, 2),
            "total_time_seconds": total_time,
            "total_time_formatted": type_manager.format_time(total_time),
            "date_range": date_range,
            "avg_distance_per_activity": (
                round(total_distance / total_activities, 2)
                if total_activities > 0
                else 0
            ),
            "avg_time_per_activity": (
                type_manager.format_time(total_time // total_activities)
                if total_activities > 0
                else "0:00"
            ),
        },
        "type_breakdown": type_stats,
    }

    output_file = output_dir / "analysis_overview.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(overview, f, ensure_ascii=False, indent=2)

    print(f"✅ 分析概览已保存到: {output_file}")
    return overview


def main():
    parser = argparse.ArgumentParser(description="生成运动数据分析")
    parser.add_argument(
        "--type",
        choices=["all", "types", "basic", "advanced", "summary", "overview"],
        default="all",
        help="生成分析类型",
    )

    args = parser.parse_args()

    print("🚀 开始生成运动数据分析...")
    print(f"📊 分析类型: {args.type}")

    # 加载活动数据
    activities = load_activities_from_db()
    if not activities:
        print("❌ 没有活动数据，退出程序")
        return 1

    # 确保输出目录存在
    output_dir = ensure_output_dir()

    try:
        if args.type in ["all", "types"]:
            generate_activity_types(activities, output_dir)

        if args.type in ["all", "basic"]:
            generate_basic_statistics(activities, output_dir)

        if args.type in ["all", "advanced"]:
            generate_advanced_analysis(activities, output_dir)

        if args.type in ["all", "summary"]:
            generate_recent_summary(activities, output_dir)

        if args.type in ["all", "overview"]:
            generate_analysis_overview(activities, output_dir)

        print("\n🎉 所有分析数据生成完成！")
        print(f"📂 输出目录: {output_dir}")

        return 0

    except Exception as e:
        print(f"\n❌ 生成分析数据时出错: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
