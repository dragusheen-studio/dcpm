from .base import BaseCommand
from colorama import Fore

class InitCommand(BaseCommand):
    def run(self, params):
        self.display_info("init", params)

    def get_short_help(self):
        return "Initialize a new C++ project or library."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm init [project_name]{Fore.RESET}\n\n"
                "Starts an interactive wizard to set up your project structure.\n"
                "Configurable options:\n"
                "  - Target type (Executable or Library)\n"
                "  - C++ Standard (11, 14, 17, 20, 23)\n"
                "  - Source and Header directory naming\n"
                "  - Unit Testing support and Clang-format setup")
