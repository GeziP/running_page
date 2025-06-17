import os
import gpxpy
import json
from rich.console import Console
from rich.table import Table
import glob
from datetime import datetime, timedelta, timezone

console = Console()

# Configuration
GPX_DIRECTORY = "GPX_OUT"
ACTIVITIES_FILE = "src/static/activities.json"
# Speed threshold in km/h to distinguish running from cycling
SPEED_THRESHOLD_KMH = 18

def get_gpx_times(gpx_dir):
    """Scan all GPX files and return a map from start time to file path."""
    gpx_files = glob.glob(os.path.join(gpx_dir, "*.gpx"))
    time_to_path = {}
    for file_path in gpx_files:
        try:
            with open(file_path, "r", encoding="utf-8") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                if gpx.time:
                    gpx_time_utc = gpx.time.replace(tzinfo=timezone.utc)
                    time_to_path[gpx_time_utc] = file_path
        except Exception as e:
            # console.print(f"Error parsing {file_path}: {e}", style="red")
            pass
    return time_to_path

def find_gpx_file_by_time(activity_time, gpx_times):
    """Find a GPX file with a start time close to the activity time."""
    for gpx_time, file_path in gpx_times.items():
        # Using a tolerance of 1 minute for matching
        if abs((activity_time - gpx_time).total_seconds()) < 60:
            return file_path
    return None

def get_gpx_file_path(activity_id):
    """Constructs the GPX file path from activity ID."""
    return os.path.join(GPX_DIRECTORY, f"{activity_id}.gpx")

def get_average_speed_from_gpx(file_path):
    """
    Parses a GPX file and calculates the average moving speed in km/h.
    Returns None if the file can't be parsed or has no moving data.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            moving_data = gpx.get_moving_data()
            if moving_data is None:
                return None
            # get_moving_data returns speed in m/s
            return moving_data.speed * 3.6
    except Exception:
        return None

def classify_activity_by_speed(speed_kmh):
    """Classifies activity type based on speed."""
    if speed_kmh is None:
        return "Unknown"
    return "Cycling" if speed_kmh > SPEED_THRESHOLD_KMH else "Run"

def main():
    """
    Main function to classify activities and update the JSON file.
    """
    console.print(f"🚀 [bold green]开始智能分类活动类型[/bold green]")
    console.print(f"⚡️ 速度阈值: [bold cyan]{SPEED_THRESHOLD_KMH} km/h[/bold cyan] (高于此值为骑行)")

    try:
        with open(ACTIVITIES_FILE, "r", encoding="utf-8") as f:
            activities = json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]错误: activities.json 文件未找到 at '{ACTIVITIES_FILE}'[/bold red]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("日期")
    table.add_column("原类型")
    table.add_column("平均速度 (km/h)")
    table.add_column("推断类型")
    table.add_column("状态")

    gpx_times = get_gpx_times(GPX_DIRECTORY)
    console.print(f"🗺️  Found {len(gpx_times)} GPX files with valid time in '{GPX_DIRECTORY}'")

    activities_to_update = []
    for activity in activities:
        # We only care about activities currently classified as running types
        activity_type = activity.get("type")
        if activity_type not in ["Run", "running", "trail_running"]:
            continue

        try:
            activity_time_utc = datetime.strptime(activity["start_date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            # Handle cases where the format might be different or invalid
            continue

        gpx_file_path = find_gpx_file_by_time(activity_time_utc, gpx_times)

        if not gpx_file_path:
            continue

        average_speed_kmh = get_average_speed_from_gpx(gpx_file_path)
        original_type = activity.get("type", "N/A")

        # 调试输出
        if average_speed_kmh is not None:
            console.print(f"调试: ID {activity['run_id']}, GPX: {os.path.basename(gpx_file_path)}, 速度: {average_speed_kmh:.2f} km/h")

        inferred_type = original_type
        status = "[yellow]未处理[/yellow]"

        if average_speed_kmh is None:
            speed_str = "[red]N/A[/red]"
            status = "[red]无速度数据[/red]"
        else:
            speed_str = f"{average_speed_kmh:.2f}"
            if average_speed_kmh > SPEED_THRESHOLD_KMH:
                inferred_type = "Cycling"
                if inferred_type != activity.get("type"):
                    activities_to_update.append((activity["run_id"], inferred_type))
                    status = "[green]待更新[/green]"
                else:
                    status = "[blue]类型匹配[/blue]"
            else:
                inferred_type = "Run"
                status = "[bright_black]速度正常[/bright_black]"

        table.add_row(
            str(activity["run_id"]),
            activity["start_date_local"].split("T")[0],
            original_type,
            speed_str,
            inferred_type,
            status,
        )

    console.print(table)

    if activities_to_update:
        # Create a map of run_id to new_type for efficient update
        update_map = {run_id: new_type for run_id, new_type in activities_to_update}

        for activity in activities:
            if activity["run_id"] in update_map:
                activity["type"] = update_map[activity["run_id"]]

        try:
            with open(ACTIVITIES_FILE, "w", encoding="utf-8") as f:
                json.dump(activities, f, indent=4, ensure_ascii=False)
            console.print(f"\n✅ [bold green]成功更新 {len(activities_to_update)} 项活动类型！[/bold green]")
            console.print(f"💾 文件已保存到: [cyan]{ACTIVITIES_FILE}[/cyan]")
        except Exception as e:
            console.print(f"\n[bold red]错误: 写入 activities.json 文件失败: {e}[/bold red]")
    else:
        console.print("\n✅ [bold]所有 'Run' 类型活动的速度均低于阈值，无需更新。[/bold]")


if __name__ == "__main__":
    main() 