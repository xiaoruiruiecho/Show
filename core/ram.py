import psutil
from . import constant


def get_ram():
    ram = psutil.virtual_memory()

    return {
        "total": ram.total / 1024 ** 3,
        "used": ram.available / 1024 ** 3,
        "free": ram.free / 1024 ** 3,
        "usage": ram.percent
    }


def get_user_ram_stats(user_stats):
    """统计每个用户的内存使用情况"""
    usernames = user_stats.keys()

    for proc in psutil.process_iter(["username", "memory_info"]):
        try:
            info = proc.info
            username = info["username"]
            if username is None or username not in usernames:
                continue

            user_vram = info["memory_info"].rss / 1024 ** 3
            user_stats[username]["usage"]["ram"] += user_vram
            user_stats[constant.TOTAL_USERNAME]["usage"]["ram"] += user_vram
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return user_stats
