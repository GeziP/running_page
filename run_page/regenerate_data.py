#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_page.utils import make_activities_file


def main():
    """重新生成活动数据文件"""
    print("🔄 重新生成活动数据文件...")
    print("使用修复后的GPX类型读取功能")

    # 修改路径为正确的相对路径
    make_activities_file("data.db", "./GPX_OUT", "./src/static/activities.json", "gpx")

    print("✅ 活动数据文件已重新生成")
    print("📍 输出文件: ./src/static/activities.json")


if __name__ == "__main__":
    main()
