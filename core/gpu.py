import psutil
import warnings

import constant

warnings.filterwarnings("ignore", category=FutureWarning, message=".*pynvml.*")
import pynvml


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


def get_default_gpu_stats(users):
    gpus = get_gpus()
    gpu_count = len(gpus)
    gpu_stats = {}

    for i in range(gpu_count):
        gpu_stats[f"{i}"] = {
            "gpu_name": gpus[i]["gpu_name"],
            "total_vram": gpus[i]["total_vram"],
            "power_limit": gpus[i]["power_limit"],
            "usage": {
                "users": {}
            }
        }
        for user in users:
            gpu_stats[f"{i}"]["usage"]["util"] = 0.
            gpu_stats[f"{i}"]["usage"]["power"] = 0.
            gpu_stats[f"{i}"]["usage"]["users"][f"{user['username']}"] = 0.  # VRAM

    return gpu_stats


def get_user_gpu_stats(user_stats):
    """统计各用户对每个GPU的显存使用情况"""
    # TODO: 统计每个GPU的各用户使用情况
    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()

    for gpu_id in range(gpu_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
        try:
            procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            print(e)
            continue

        for p in procs:
            try:
                proc = psutil.Process(p.pid)
                username = proc.username()
                user_gpu = p.usedGpuMemory / 1024 ** 3
                user_stats[username]["usage"][f"gpu{gpu_id}"] += user_gpu
                user_stats[constant.TOTAL_USERNAME]["usage"][f"gpu{gpu_id}"] += user_gpu
            except psutil.NoSuchProcess:
                continue
            except Exception as e:
                print(e)
                continue

    pynvml.nvmlShutdown()
    return user_stats


def get_gpu_user_stats(gpu_stats):
    pynvml.nvmlInit()
    gpu_count = len(gpu_stats)

    for gid in range(gpu_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(gid)
        try:
            procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            print(e)
            continue

        usage = gpu_stats[f"{gid}"]["usage"]
        usage["util"] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        usage["power"] = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
        for p in procs:
            try:
                proc = psutil.Process(p.pid)
                username = proc.username()
                usage["users"][f"{username}"] += p.usedGpuMemory / 1024 ** 3
            except psutil.NoSuchProcess:
                continue
            except Exception as e:
                print(e)
                continue

    pynvml.nvmlShutdown()
    return gpu_stats
