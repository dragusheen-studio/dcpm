import os
import json
from abc import ABC, abstractmethod
from colorama import Fore, Style

class BaseCommand(ABC):
    _config_path = ".dcpm/config.json"

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
        if not os.path.exists(self._config_path):
            print(f"{Fore.RED}Error: Not a DCPM project or not at the root of the project.{Fore.RESET}")
            return False
        return True
    
    def get_dcpm_config(self):
        try:
            with open(self._config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"{Fore.RED}Error: Could not read {self._config_path} ({e}){Fore.RESET}")
            return None
