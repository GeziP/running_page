#!/usr/bin/env python3
import json

# 读取activities.json
with open('src/static/activities.json', 'r', encoding='utf-8') as f:
    activities = json.load(f)

print("修正高速活动为cycling类型...")

# 创建备份
import shutil
shutil.copy('src/static/activities.json', 'src/static/activities.json.backup2')
print("已创建备份文件: activities.json.backup2")

cycling_count = 0
for activity in activities:
    # 如果是Run类型且速度超过15km/h，改为cycling
    if activity.get('type') == 'Run':
        speed_ms = activity.get('average_speed', 0)
        speed_kmh = speed_ms * 3.6
        
        if speed_kmh > 15:  # 15km/h以上认为是自行车
            print(f"修正活动 {activity['run_id']}: Run -> cycling (速度: {speed_kmh:.1f}km/h)")
            activity['type'] = 'cycling'
            cycling_count += 1

# 保存修正后的文件
with open('src/static/activities.json', 'w', encoding='utf-8') as f:
    json.dump(activities, f, ensure_ascii=False, indent=2)

# 统计最终结果
type_counts = {}
for activity in activities:
    activity_type = activity.get('type', 'Unknown')
    type_counts[activity_type] = type_counts.get(activity_type, 0) + 1

print(f"\n修正结果:")
print(f"  修正了 {cycling_count} 个活动为cycling类型")
print(f"\n最终类型分布:")
for activity_type, count in sorted(type_counts.items()):
    print(f"  {activity_type}: {count}")

print("\n已保存修正后的activities.json") 