import psutil


def get_user_cpu_stats(user_stats):
    """统计每个用户的CPU使用情况"""
    usernames = user_stats.keys()

    for proc in psutil.process_iter(["username", "cpu_percent"]):
        try:
            info = proc.info
            username = info["username"]
            if username is None or username not in usernames:
                continue

            user_stats[username]["usage"]["cpu"] += info["cpu_percent"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return user_stats