import os
import json
import subprocess
from colorama import Fore, Style
from .base import BaseCommand
from .build import BuildCommand

class RunCommand(BaseCommand):
    _build_dir = "build"

    def run(self, params):
        if not self.dcpm_validation(): return

        if "--noBuild" not in params:
            builder = BuildCommand()
            builder.run(params)
        self._execute_section(params)

    def _execute_section(self, params):
        config = self.get_dcpm_config()
        if not config: return

        project_name = config.get("name")
        target_type = config.get("target_type")
        
        binary_to_run = os.path.join(self._build_dir, project_name)

        if target_type in ["Library", "Header-only"]:
            binary_to_run = os.path.join(self._build_dir, f"{project_name}_playground")

        if "--test" in params:
            binary_to_run = os.path.join(self._build_dir, "UnitTests")

        if os.path.exists(binary_to_run):
            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}--- Running: {os.path.basename(binary_to_run)} ---{Style.RESET_ALL}\n")
            try:
                subprocess.run([f"./{binary_to_run}"])
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Process interrupted by user.{Fore.RESET}")
        else:
            print(f"{Fore.RED}Error: Executable '{binary_to_run}' not found.{Fore.RESET}")
            print(f"{Fore.YELLOW}Hint: Try running without --noBuild to compile the target.{Fore.RESET}")

    def get_short_help(self):
        return "Build and execute the project targets."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm run [options]{Fore.RESET}\n\n"
                "Options:\n"
                "  --test     : Run the UnitTests suite instead of the main binary.\n"
                "  --noBuild  : Skip the build phase and run the existing binary.\n"
                "  --reset    : Perform a hard clean (passed to build) before running.\n"
                "  --clean    : Perform a soft clean (passed to build) before running.\n\n"
                f"{Style.BRIGHT}Note:{Style.RESET_ALL} For Libraries, this runs the playground application.")
