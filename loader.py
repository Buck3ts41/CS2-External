import psutil
import time
import os
from colorama import Fore, Style
from sara import CS2Esp

def clear_console():
    os.system("cls")

def print_banner():
    clear_console()
    print(Fore.CYAN + """
                                                   
  .--.--.                                           
 /  /    '.                                         
|  :  /`. /              __  ,-.                   
;  |  |--`             ,' ,'/ /|                   
|  :  ;_      ,--.--.  '  | |' | ,--.--.          
 \  \    `.  /       \ |  |   ,'/       \         
  `----.   \.--.  .-. |'  :  / .--.  .-. |        
  __ \  \  | \__\/ : . .|  | '   \__\/ : . .       
 /  /`--'  / ," .--.; ||  , ;  /  /`--'  /       
'--'.     / /  /  ,.  ||  , ;  /  /  ,.  |       
  `--'---' ;  :   .'   \---'  ;  :   .'   \      
           |  ,     .-./      |  ,     .-./      
            `--`---'           `--`---'          

""" + Style.RESET_ALL, '\n')
    print(Fore.CYAN + "[*] By Buck3ts41", '\n', Style.RESET_ALL)
    time.sleep(2)
    clear_console()

def check_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if process_name.lower() in proc.info['name'].lower():
            return True
    return False

def main():
    print_banner()
    input(Fore.YELLOW + "---> Press ENTER in game <---" + Style.RESET_ALL)

    if check_process_running('cs2'):
        clear_console()
        print('[+] CS2 is running, starting Sara...')
        esp = CS2Esp()
        esp.run()
    else:
        print(Fore.RED + "[!] Process not found or need to Update Offsets" + Style.RESET_ALL)
        time.sleep(3)
        exit(0)

if __name__ == "__main__":
    main()
