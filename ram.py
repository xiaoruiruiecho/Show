import psutil


def get_user_ram_stats(user_stats):
    """统计每个用户的内存使用情况"""
    usernames = user_stats.keys()

    for proc in psutil.process_iter(["username", "memory_info"]):
        try:
            info = proc.info
            username = info["username"]
            if username is None or username not in usernames:
                continue

            # 常驻内存
            user_stats[username]["usage"]["ram"] += info["memory_info"].rss / 1024 ** 3
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return user_stats