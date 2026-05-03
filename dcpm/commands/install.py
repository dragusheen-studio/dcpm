from .base import BaseCommand
from colorama import Fore

class InstallCommand(BaseCommand):
    def run(self, params):
        self.display_info("install", params)

    def get_short_help(self):
        return "Install all project dependencies."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm install{Fore.RESET}\n\n"
                "Reads the '.dcpm/config.json' file and ensures all dependencies\n"
                "are present in the '.dcpm/modules/' directory.\n"
                "Essential after cloning an existing DCPM project.")
