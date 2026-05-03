from .base import BaseCommand
from colorama import Fore

class RunCommand(BaseCommand):
    def run(self, params):
        self.display_info("run", params)

    def get_short_help(self):
        return "Build and run the project executable."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm run{Fore.RESET}\n\n"
                "Automates the C++ development workflow:\n"
                "  1. Generates build files via CMake\n"
                "  2. Compiles the project using the available build tool\n"
                "  3. Executes the resulting binary.")
