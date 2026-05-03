from .base import BaseCommand
from colorama import Fore

class AddCommand(BaseCommand):
    def run(self, params):
        self.display_info("add", params)

    def get_short_help(self):
        return "Add a new dependency to the project."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm add <git_url_or_name>{Fore.RESET}\n\n"
                "Clones a library from a Git repository into '.dcpm/modules/'.\n"
                "Automatically updates project configuration and CMake links.")
