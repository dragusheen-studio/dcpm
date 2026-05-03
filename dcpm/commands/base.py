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
