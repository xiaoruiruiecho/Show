#!/usr/bin/env python3
import argparse
from prettytable import PrettyTable
from colorama import Fore

from core import constant
from core.cpu import get_user_cpu_stats
from core.disk import get_hdds, get_ssd, get_user_ssd_stats, get_user_hdd_stats
from core.gpu import get_user_gpu_stats, get_gpu_user_stats, get_gpus, get_default_gpu_stats
from core.ram import get_ram, get_user_ram_stats
from core.user import get_users, get_default_user_stats
from core.utils import colornum, colorstr


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
        if user == constant.TOTAL_USERNAME:
            table_item = [colorstr(constant.TOTAL_USERNAME, color=Fore.RED),
                          colorstr(constant.TOTAL_USERNAME, color=Fore.RED)]
        else:
            table_item = [user, userinfo["nickname"]]
        usage = userinfo["usage"]

        if show_flag["cpu"] or show_all:
            cpu = usage["cpu"]
            if user == constant.TOTAL_USERNAME:
                table_item.append(colornum(cpu, 50, 80))
            else:
                table_item.append(colornum(cpu, 20, 50))
        if show_flag["ram"] or show_all:
            ram = usage["ram"]
            if user == constant.TOTAL_USERNAME:
                table_item.append(
                    colornum(ram, RAM['total'] * 0.5, RAM['total'] * 0.8) + f" GB / {RAM['total']:.2f} GB")
            else:
                table_item.append(
                    colornum(ram, RAM['total'] * 0.2, RAM['total'] * 0.5) + f" GB / {RAM['total']:.2f} GB")
        if show_flag["gpu"] or show_all:
            gpus_vram = [usage[f"gpu{gid}"] for gid in range(gpu_count)]
            if user == constant.TOTAL_USERNAME:
                table_item += [colornum(gpus_vram[i],
                                        GPUs[i]['total_vram'] * 0.5,
                                        GPUs[i]['total_vram'] * 0.8) + f" GB / {GPUs[i]['total_vram']:.2f} GB"
                               for i in range(len(gpus_vram))]
            else:
                table_item += [colornum(gpus_vram[i],
                                        GPUs[i]['total_vram'] * 0.2,
                                        GPUs[i]['total_vram'] * 0.5) + f" GB / {GPUs[i]['total_vram']:.2f} GB"
                               for i in range(len(gpus_vram))]
        if show_flag["ssd"] or show_all:
            ssd = usage["ssd"]
            if user == constant.TOTAL_USERNAME:
                table_item.append(
                    colornum(ssd, SSD['total'] * 1024 * 0.5,
                             SSD['total'] * 1024 * 0.8) + f" GB / {SSD['total']:.2f} TB")
            else:
                table_item.append(
                    colornum(ssd, SSD['total'] * 1024 * 0.1,
                             SSD['total'] * 1024 * 0.3) + f" GB / {SSD['total']:.2f} TB")
        if show_flag["hdd"] or show_all:
            hdds = [usage[f"hdd{i}"] for i in range(len(HDDs))]
            if user == constant.TOTAL_USERNAME:
                table_item += [
                    colornum(hdds[i], HDDs[i]['total'] * 1024 * 0.5,
                             HDDs[i]['total'] * 1024 * 0.8) + f" GB / {HDDs[i]['total']:.2f} TB"
                    for i in range(len(hdds))]
            else:
                table_item += [
                    colornum(hdds[i], HDDs[i]['total'] * 1024 * 0.1,
                             HDDs[i]['total'] * 1024 * 0.3) + f" GB / {HDDs[i]['total']:.2f} TB"
                    for i in range(len(hdds))]

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
        if used_gpu_vram > 1e-2:
            used_users.append(user)

    users = used_users
    headers = ["GPU ID", "GPU NAME", "Util (%)", "Power (W)", "VRAM (GB)"]
    headers += [f"{user['nickname']} VRAM (GB)" for user in users]
    headers += ["Available VRAM (GB)"]

    table = PrettyTable(headers)
    for gpu, gpuinfo in gpu_stats.items():
        usage = gpuinfo["usage"]
        table_item = [gpu,
                      gpuinfo["gpu_name"],
                      colornum(usage['util'], 50, 80),
                      colornum(usage['power'], gpuinfo['power_limit'] * 0.5, gpuinfo['power_limit'] * 0.8)
                      + f" W / {gpuinfo['power_limit']:.2f} W"]

        total_used_vram = 0.
        total_vram = gpuinfo["total_vram"]
        user_vram_list = []
        for user in users:
            user_vram = usage['users'][user['username']]
            total_used_vram += user_vram
            user_vram_list.append(colornum(user_vram,
                                           total_vram * 0.2,
                                           total_vram * 0.8) + f" GB / {total_vram:.2f} GB")

        table_item.append(colornum(total_used_vram, total_vram * 0.5, total_vram * 0.8) + f" GB / {total_vram:.2f} GB")
        table_item += user_vram_list
        table_item.append(colornum(total_vram - total_used_vram, total_vram, total_vram) + f" GB / {total_vram:.2f} GB")
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
    parser.add_argument("-j", "--json", default="/home/rui/Config/Show/config.json", type=str,
                        help="config.json所在路径")
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
