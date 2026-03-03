import psutil
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, message=".*pynvml.*")
import pynvml


def get_user_gpu_stats(user_stats):
    """统计各用户对每个GPU的显存使用情况"""
    # TODO: 统计每个GPU的各用户使用情况
    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()

    for gpu_id in range(gpu_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
        try:
            procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        except Exception as e:
            print(e)
            continue

        for p in procs:
            try:
                proc = psutil.Process(p.pid)
                username = proc.username()
                user_stats[username]["usage"][f"gpu{gpu_id}"] += p.usedGpuMemory / 1024 ** 3
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
        except Exception as e:
            print(e)
            continue

        usage = gpu_stats[f"gpu{gid}"]["usage"]
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
