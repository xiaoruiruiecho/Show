import os
import subprocess


def get_dir_size(path):
    """调用 du -s 统计目录大小 (bytes)"""
    if not os.path.exists(path):
        return 0

    try:
        result = subprocess.check_output(["du", "-sb", path], text=True)
        size = int(result.split()[0]) * 1. / 1024 ** 3
        return size
    except Exception:
        return 0


def get_user_ssd_stats(user_stats):
    """统计/home下各用户根目录的空间占用"""
    home_path = "/home"
    if not os.path.exists(home_path):
        return user_stats

    usernames = user_stats.keys()
    for entry in os.scandir(home_path):
        if entry.is_dir() and entry.name in usernames:
            user_stats[entry.name]["usage"]["ssd"] = get_dir_size(entry.path)

    return user_stats


def get_user_hdd_stats(user_stats, hdds):
    usernames = user_stats.keys()

    for username in usernames:
        hdd_sub_path = user_stats[username]["hdd_sub_path"]
        if hdd_sub_path.startswith('/'):
            hdd_sub_path = hdd_sub_path[1:]

        for i in range(len(hdds)):
            hdd = hdds[i]
            hdd_path = os.path.join(hdd["path"], hdd_sub_path)
            user_stats[username]["usage"][f"hdd{i}"] += get_dir_size(hdd_path)

    return user_stats