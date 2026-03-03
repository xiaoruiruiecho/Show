import json
import psutil
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, message=".*pynvml.*")
import pynvml


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
        system_usernames = [entry.pw_name for entry in pwd.getpwall()]

        for username in system_usernames:
            cfg = config_users.get(username, {})
            users.append({
                "username": username,
                "nickname": cfg.get("nickname", username),
                "ssd_path": cfg.get("ssd_path", f"/home/{username}"),
                "hdd_sub_path": cfg.get("hdd_sub_path", None)
            })

        return users
    except Exception as e:
        print(e)
        exit(1)

    # try:
    #     data = json.load(open(path))
    #     users = data["users"]
    #     # TODO: users校验
    #
    #     return users
    # except Exception as e:
    #     print(e)
    #     exit(1)


def get_ram():
    ram = psutil.virtual_memory()

    return {
        "total": ram.total / 1024 ** 3,
        "used": ram.available / 1024 ** 3,
        "free": ram.free / 1024 ** 3,
        "usage": ram.percent
    }


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


def get_gpu_count():
    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()
    pynvml.nvmlShutdown()

    return gpu_count


def get_gpus():
    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()
    gpus = []

    for gpu_id in range(gpu_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        total_vram = pynvml.nvmlDeviceGetMemoryInfo(handle).total / 1024 ** 3  # GB
        power_limit = pynvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000  # W

        gpus.append({
            "gpu_id": gpu_id,
            "gpu_name": gpu_name,
            "total_vram": total_vram,
            "power_limit": power_limit
        })

    pynvml.nvmlShutdown()
    return gpus


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


def get_default_gpu_stats(users):
    gpus = get_gpus()
    gpu_count = len(gpus)
    gpu_stats = {}

    for i in range(gpu_count):
        gpu_stats[f"gpu{i}"] = {
            "gpu_name": gpus[i]["gpu_name"],
            "total_vram": gpus[i]["total_vram"],
            "power_limit": gpus[i]["power_limit"],
            "usage": {
                "users": {}
            }
        }
        for user in users:
            gpu_stats[f"gpu{i}"]["usage"]["util"] = 0.
            gpu_stats[f"gpu{i}"]["usage"]["power"] = 0.
            gpu_stats[f"gpu{i}"]["usage"]["users"][f"{user['username']}"] = 0.  # VRAM

    return gpu_stats


if __name__ == "__main__":
    print("\nRAM: \n", json.dumps(get_ram(), indent=4, ensure_ascii=False))
    print("\nSSD: \n", json.dumps(get_ssd(), indent=4, ensure_ascii=False))
    print("\nHDDs: \n", json.dumps(get_hdds(), indent=4, ensure_ascii=False))
    print("\nGPU count: \n", json.dumps(get_gpu_count(), indent=4, ensure_ascii=False))
    print("\nGPUs: \n", json.dumps(get_gpus(), indent=4, ensure_ascii=False))
    print("\ndefault_user_stats: \n",
          json.dumps(get_default_user_stats(), indent=4, ensure_ascii=False))
    print("\ndefault_gpu_stats: \n",
          json.dumps(get_default_gpu_stats(), indent=4, ensure_ascii=False))
