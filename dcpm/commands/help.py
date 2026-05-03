from .base import BaseCommand
from colorama import Fore, Style

class HelpCommand(BaseCommand):
    def run(self, params):
        from . import COMMANDS
        
        if params and params[0] in COMMANDS:
            cmd_name = params[0]
            print(f"\n{Fore.CYAN}{Style.BRIGHT}DETAILED HELP: {cmd_name.upper()}{Style.RESET_ALL}")
            print("=" * 45)
            print(COMMANDS[cmd_name].get_long_help())
            print("=" * 45)
        else:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}DCPM - Dragusheen C++ Project Manager{Style.RESET_ALL}")
            print(f"Making C++ development as easy as modern Web tooling.\n")
            print(f"{Style.BRIGHT}Available Commands:{Style.RESET_ALL}")
            
            for name, cmd in COMMANDS.items():
                print(f"  {Fore.GREEN}{name:<12}{Fore.RESET} : {cmd.get_short_help()}")
            
            print(f"\nType {Fore.YELLOW}dcpm help <command>{Fore.RESET} for detailed information.")

    def get_short_help(self):
        return "Display global or command-specific help."

    def get_long_help(self):
        return ("Usage: dcpm help [command]\n\n"
                "Shows the list of available commands or provides detailed documentation\n"
                "on how to use a specific command.")
