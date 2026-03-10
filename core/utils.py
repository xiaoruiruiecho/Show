from colorama import Fore, Style, init

init(autoreset=True)


def colorstr(string, color, fmt="{}"):
    return f"{color}{fmt.format(string)}{Style.RESET_ALL}"


def colornum(val, low, high, fmt="{:.2f}", reverse=False):
    val = abs(val)
    if not reverse:
        if val < 1e-2:
            return fmt.format(val)
        elif val < low:
            return f"{Fore.GREEN}{fmt.format(val)}{Style.RESET_ALL}"
        elif val < high:
            return f"{Fore.YELLOW}{fmt.format(val)}{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}{fmt.format(val)}{Style.RESET_ALL}"
    else:
        if val > high:
            return f"{Fore.GREEN}{fmt.format(val)}{Style.RESET_ALL}"
        elif val > low:
            return f"{Fore.YELLOW}{fmt.format(val)}{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}{fmt.format(val)}{Style.RESET_ALL}"
