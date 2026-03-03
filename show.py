#!/usr/bin/env python3
import argparse
from prettytable import PrettyTable

from cpu import get_user_cpu_stats
from disk import get_user_ssd_stats, get_user_hdd_stats
from gpu import get_user_gpu_stats, get_gpu_user_stats
from ram import get_user_ram_stats
from utils import get_default_user_stats, get_hdds, get_gpus, get_default_gpu_stats, get_users, get_ram, get_ssd


def show_user_stats(user_stats, show_flag,
                    SSD=get_ssd(), RAM=get_ram(), GPUs=get_gpus(), HDDs=get_hdds()):
    print()

    gpu_count = len(GPUs)
    show_all = show_flag["all"]
    headers = ["User", "Name"]
    if show_flag["cpu"] or show_all:
        headers.append("CPU (%)")
    if show_flag["ram"] or show_all:
        headers.append("RAM (GB)")
    if show_flag["gpu"] or show_all:
        headers += [f"GPU {gid} VRAM (GB)" for gid in range(gpu_count)]
    if show_flag["ssd"] or show_all:
        headers.append("SSD (GB)")
    if show_flag["hdd"] or show_all:
        headers += [f"HDD {i} (GB)" for i in range(len(HDDs))]

    table = PrettyTable(headers)
    for user, userinfo in user_stats.items():
        table_item = [user, userinfo["nickname"]]
        usage = userinfo["usage"]
        
        if show_flag["cpu"] or show_all:
            cpu = usage["cpu"]
            table_item.append(f"{cpu:.2f} %")
        if show_flag["ram"] or show_all:
            ram = usage["ram"]
            table_item.append(f"{ram:.2f} GB / {RAM['total']:.2f} GB")
        if show_flag["gpu"] or show_all:
            gpus_vram = [usage[f"gpu{gid}"] for gid in range(gpu_count)]
            table_item += [f"{gpus_vram[i]:.2f} GB / {GPUs[i]['total_vram']:.2f} GB" for i in range(len(gpus_vram))]
        if show_flag["ssd"] or show_all:
            ssd = usage["ssd"]
            table_item.append(f"{ssd:.2f} GB / {SSD['total']:.2f} TB")
        if show_flag["hdd"] or show_all:
            hdds = [usage[f"hdd{i}"] for i in range(len(HDDs))]
            table_item += [f"{hdds[i]:.2f} GB / {HDDs[i]['total']:.2f} TB" for i in range(len(hdds))]

        table.add_row(table_item)

    print(table)
    print()


def show_gpu_stats(gpu_stats, show_flag, users):
    print()
    if not show_flag["GPU"]:
        return

    used_users = []
    for user in users:
        used_gpu_vram = 0.
        for gpu, gpuinfo in gpu_stats.items():
            used_gpu_vram += gpuinfo["usage"]["users"][user["username"]]
        if used_gpu_vram > 1.:
            used_users.append(user)

    users = used_users
    headers = ["GPU ID", "GPU NAME", "Util (%)", "Power (W)"]
    headers += [f"{user['nickname']} VRAM (GB)" for user in users]
    headers.append("其他用户 VRAM (GB)")

    table = PrettyTable(headers)
    for gpu, gpuinfo in gpu_stats.items():
        usage = gpuinfo["usage"]
        table_item = [gpu,
                      gpuinfo["gpu_name"],
                      f"{usage['util']:.2f}",
                      f"{usage['power']:.2f} W / {gpuinfo['power_limit']:.2f} W"]

        total_vram = gpuinfo["total_vram"]
        for user in users:
            table_item.append(f"{usage['users'][user['username']]:.2f} GB / {total_vram:.2f} GB")

        table_item.append(f"< 1.00 GB / {total_vram:.2f} GB")
        table.add_row(table_item)

    print(table)
    print()


def main():
    parser = argparse.ArgumentParser(description="资源占用统计工具")
    parser.add_argument("-c", "--cpu", action="store_true", help="展示CPU基本使用情况")
    parser.add_argument("-g", "--gpu", action="store_true", help="展示GPU基本使用情况")
    parser.add_argument("-r", "--ram", action="store_true", help="展示内存基本使用情况")
    parser.add_argument("-d", "--disk", action="store_true", help="展示硬盘基本使用情况")
    parser.add_argument("-a", "--all", action="store_true", help="展示所有资源基本使用情况")
    parser.add_argument("-G", "--GPU", action="store_true", help="展示GPU详细使用情况")
    parser.add_argument("-j", "--json", default="/home/rui/Config/Show/config.json", action="store_true", help="config.json所在路径")
    args = parser.parse_args()

    print("Loading ......")

    users = get_users(args.json)
    SSD = get_ssd()
    RAM = get_ram()
    GPUs = get_gpus()
    HDDs = get_hdds()
    user_stats = get_default_user_stats(users)
    gpu_stats = get_default_gpu_stats(users)
    show_all = False
    show_flag = {
        "cpu": False,
        "ram": False,
        "gpu": False,
        "ssd": False,
        "hdd": False,
        "all": False,
        "GPU": False
    }

    # 默认展示CPU和RAM
    args_copy = vars(args).copy()
    args_copy.pop('json', None)
    if not any(args_copy.values()):
        user_stats = get_user_cpu_stats(user_stats)
        show_flag["cpu"] = True
        user_stats = get_user_ram_stats(user_stats)
        show_flag["ram"] = True

        show_user_stats(user_stats, show_flag, SSD=SSD, RAM=RAM, GPUs=GPUs, HDDs=HDDs)
    else:
        main_args = ["cpu", "gpu", "ram", "disk", "all"]
        if any(getattr(args, arg) for arg in main_args):
            if args.all:
                show_flag["all"] = True
                show_all = True
            if args.cpu or show_all:
                user_stats = get_user_cpu_stats(user_stats)
                show_flag["cpu"] = True
            if args.gpu or show_all:
                user_stats = get_user_gpu_stats(user_stats)
                show_flag["gpu"] = True
            if args.ram or show_all:
                user_stats = get_user_ram_stats(user_stats)
                show_flag["ram"] = True
            if args.disk or show_all:
                user_stats = get_user_ssd_stats(user_stats)
                show_flag["ssd"] = True
                user_stats = get_user_hdd_stats(user_stats, HDDs)
                show_flag["hdd"] = True

            show_user_stats(user_stats, show_flag, SSD=SSD, RAM=RAM, GPUs=GPUs, HDDs=HDDs)

        if args.GPU:
            show_flag["GPU"] = True
            gpu_stats = get_gpu_user_stats(gpu_stats)
            show_gpu_stats(gpu_stats, show_flag, users)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        exit(1)


"""
Windows:
pyinstaller --onefile --add-data "cpu.py;." --add-data "disk.py;." --add-data "gpu.py;." --add-data "ram.py;." --add-data "utils.py;." show.py

Linux:
# Ubuntu22只有libffi7, 没有libffi6
wget http://archive.ubuntu.com/ubuntu/pool/main/libf/libffi/libffi6_3.2.1-8_amd64.deb
sudo dpkg -i libffi6_3.2.1-8_amd64.deb

pyinstaller --onefile --add-data "cpu.py:." --add-data "disk.py:." --add-data "gpu.py:." --add-data "ram.py:." --add-data "utils.py:." show.py
sudo cp dist/show /usr/local/bin/show
sudo chown root:root /usr/local/bin/show
sudo chmod u+s,+x /usr/local/bin/show

ls -l /usr/local/bin/show  # -rwsr-xr-x
"""