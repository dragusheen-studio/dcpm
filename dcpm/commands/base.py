import os
import json
from abc import ABC, abstractmethod
from colorama import Fore

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
