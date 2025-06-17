#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import glob
import os


def check_gpx_types():
    """检查GPX文件中的type字段"""

    gpx_files = glob.glob("GPX_OUT/*.gpx")
    print(f"找到 {len(gpx_files)} 个GPX文件，开始全面检查...")

    type_counts = {}
    sample_files = {}

    for i, gpx_file in enumerate(gpx_files):  # 检查所有文件
        try:
            tree = ET.parse(gpx_file)
            root = tree.getroot()

            # 查找type元素
            type_elem = root.find(".//{http://www.topografix.com/GPX/1/1}type")
            if type_elem is not None and type_elem.text:
                gpx_type = type_elem.text.strip().lower()  # 转换为小写以合并同类项
                type_counts[gpx_type] = type_counts.get(gpx_type, 0) + 1

                # 记录每种类型的示例文件
                if gpx_type not in sample_files:
                    sample_files[gpx_type] = []
                if len(sample_files[gpx_type]) < 3:
                    file_id = os.path.basename(gpx_file).replace(".gpx", "")
                    sample_files[gpx_type].append(file_id)
            else:
                type_counts["none"] = type_counts.get("none", 0) + 1

        except Exception as e:
            # print(f"解析文件 {gpx_file} 时出错: {e}")
            type_counts["error"] = type_counts.get("error", 0) + 1

    print(f"\nGPX文件中的type字段统计 (共 {len(gpx_files)} 个文件):")
    for gpx_type, count in sorted(type_counts.items()):
        print(f"  - {gpx_type}: {count} 个文件")
        if gpx_type in sample_files and sample_files[gpx_type]:
            print(f"    示例文件ID: {', '.join(sample_files[gpx_type])}")


if __name__ == "__main__":
    check_gpx_types()
