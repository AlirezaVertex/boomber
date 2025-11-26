import colorama
colorama.init()


def print_success(data):
    print(colorama.Fore.GREEN + f'[+] {data}' + colorama.Fore.RESET)
    
def print_warning(data):
    print(colorama.Fore.YELLOW + f'[!] {data}' + colorama.Fore.RESET)
    
def print_error(data):
    print(colorama.Fore.RED + f'[-] {data}' + colorama.Fore.RESET)