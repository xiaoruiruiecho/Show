from colorama import Fore, Style, init

init(autoreset=True)


def colorize(val, low, high, fmt="{:.2f}"):
    if abs(val) < 1e-9:
        return fmt.format(val)
    elif val < low:
        return f"{Fore.GREEN}{fmt.format(val)}{Style.RESET_ALL}"
    elif val < high:
        return f"{Fore.YELLOW}{fmt.format(val)}{Style.RESET_ALL}"
    else:
        return f"{Fore.RED}{fmt.format(val)}{Style.RESET_ALL}"
