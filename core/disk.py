import os
import psutil
import subprocess
from . import constant


def get_ssd():
    data = psutil.disk_partitions(all=False)
    ssd = {
        "total": 0.,
        "used": 0.,
        "free": 0.,
        "usage": 0.
    }

    for disk in data:
        if not disk.device.startswith("/dev/") or "/dev/sd" in disk.device:
            continue
        if "/dev/sd" in disk.device:
            continue

        try:
            usage = psutil.disk_usage(disk.mountpoint)
        except PermissionError:
            continue

        ssd["total"] += usage.total / 1023 ** 4
        ssd["used"] += usage.used / 1023 ** 4
        ssd["free"] += usage.free / 1023 ** 4

    if ssd["total"] > 1:
        ssd["usage"] = ssd["used"] / ssd["total"]

    return ssd


def get_hdds():
    data = psutil.disk_partitions(all=False)
    hdds = []

    for disk in data:
        if "/dev/sd" in disk.device:
            try:
                usage = psutil.disk_usage(disk.mountpoint)
                hdds.append({
                    "device": disk.device,
                    "path": disk.mountpoint,
                    "type": disk.fstype,
                    "total": usage.total / 1024 ** 4,
                    "used": usage.used / 1024 ** 4,
                    "free": usage.free / 1024 ** 4,
                    "usage": usage.percent
                })
            except PermissionError:
                # 有些挂载点可能权限不足
                continue

    return hdds


def get_dir_size(path):
    if not os.path.exists(path):
        return 0

    try:
        result = subprocess.run(
            ["du", "-sb", path],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False
        )

        if result.stdout:
            return int(result.stdout.split()[0]) / 1024 ** 3
        return 0
    except Exception as e:
        print(e)
        return 0


def get_user_ssd_stats(user_stats):
    """统计/home下各用户根目录的空间占用"""
    home_path = "/home"
    if not os.path.exists(home_path):
        return user_stats

    usernames = user_stats.keys()
    for entry in os.scandir(home_path):
        if entry.is_dir() and entry.name in usernames:
            user_ssd = get_dir_size(entry.path)
            user_stats[entry.name]["usage"]["ssd"] = user_ssd
            user_stats[constant.TOTAL_USERNAME]["usage"]["ssd"] += user_ssd

    return user_stats


def get_user_hdd_stats(user_stats, hdds):
    usernames = user_stats.keys()

    for username in usernames:
        hdd_sub_path = user_stats[username]["hdd_sub_path"]
        if hdd_sub_path is None:
            if username != constant.TOTAL_USERNAME:
                for i in range(len(hdds)):
                    user_stats[username]["usage"][f"hdd{i}"] = 0
        else:
            if hdd_sub_path.startswith('/'):
                hdd_sub_path = hdd_sub_path[1:]

            for i in range(len(hdds)):
                hdd = hdds[i]
                hdd_path = os.path.join(hdd["path"], hdd_sub_path)
                user_hdd = get_dir_size(hdd_path)
                user_stats[username]["usage"][f"hdd{i}"] = user_hdd
                user_stats[constant.TOTAL_USERNAME]["usage"][f"hdd{i}"] += user_hdd

    return user_stats
