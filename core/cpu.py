import time
import psutil
from . import constant


def get_user_cpu_stats(user_stats):
    """统计每个用户的CPU使用情况"""
    usernames = set(user_stats)
    procs = []

    # warmup
    for p in psutil.process_iter(["username"]):
        try:
            if p.info["username"] in usernames:
                p.cpu_percent(None)
                procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            print(e)
            exit(1)

    time.sleep(0.1)
    for p in procs:
        try:
            cpu = p.cpu_percent(None)
            user_stats[p.info["username"]]["usage"]["cpu"] += cpu
            user_stats[constant.TOTAL_USERNAME]["usage"]["cpu"] += cpu
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            print(e)
            exit(1)

    return user_stats
