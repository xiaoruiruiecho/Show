import json
import pwd

import constant
from gpu import get_gpu_count
from disk import get_hdds


def get_users(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)["users"]
        assert isinstance(data, list) and len(data) > 0
    except Exception as e:
        print(e)
        exit(1)

    config_users = {
        u.get("username"): u
        for u in data
        if isinstance(u, dict) and u.get("username")
    }

    try:
        users = []
        system_usernames = ["root"] + [entry.pw_name for entry in pwd.getpwall() if 1000 < entry.pw_uid <= 60000]

        for username in system_usernames:
            cfg = config_users.get(username, {})
            users.append({
                "username": username,
                "nickname": cfg.get("nickname", username),
                "ssd_path": cfg.get("ssd_path", f"/home/{username}"),
                "hdd_sub_path": cfg.get("hdd_sub_path", None)
            })

        users.append({
            "username": constant.TOTAL_USERNAME,
            "nickname": constant.TOTAL_USERNAME,
            "ssd_path": None,
            "hdd_sub_path": None
        })

        return users
    except Exception as e:
        print(e)
        exit(1)


def get_default_user_stats(users):
    gpu_count = get_gpu_count()
    hdds = get_hdds()
    user_stats = {}

    for user in users:
        user_stats[user["username"]] = {
            "nickname": user["nickname"],
            "hdd_sub_path": user["hdd_sub_path"],
            "usage": {
                "cpu": 0.,
                "ram": 0.,
                "ssd": 0.
            }
        }

        for gpu_id in range(gpu_count):
            user_stats[user["username"]]["usage"][f"gpu{gpu_id}"] = 0.

        for i in range(len(hdds)):
            user_stats[user["username"]]["usage"][f"hdd{i}"] = 0.

    return user_stats
