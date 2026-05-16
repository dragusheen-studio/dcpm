import os
from abc import ABC, abstractmethod
from colorama import Fore, Style

class BaseCommand(ABC):
    @abstractmethod
    def run(self, params):
        pass

    @abstractmethod
    def get_short_help(self):
        pass

    @abstractmethod
    def get_long_help(self):
        pass

    def display_info(self, cmd_name, params):
        print(f"{Fore.CYAN}{Style.BRIGHT}Command:{Style.RESET_ALL} {cmd_name}")
        if params:
            print(f"{Fore.YELLOW}Parameters:")
            for p in params:
                print(f"    - {p}")
        else:
            print(f"{Fore.YELLOW}Parameters:{Style.RESET_ALL} None")

    def dcpm_validation(self):
        if not os.path.exists(".dcpm/config.json"):
            print(f"{Fore.RED}Error: Not a DCPM project or not at the root of the project.{Fore.RESET}")
            return False
        return True
