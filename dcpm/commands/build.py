import os
import subprocess
import sys
import shutil
from colorama import Fore, Style
from .base import BaseCommand

class BuildCommand(BaseCommand):
    _build_dir = "build"

    def run(self, params):
        if not self.dcpm_validation(): return

        self._clean_section(params)
        self._build_section(params)

    def _clean_section(self, params):
        should_reset = "--reset" in params
        should_clean = "--clean" in params

        if should_reset:
            if os.path.exists(self._build_dir):
                print(f"{Fore.YELLOW}Resetting: Removing build directory...{Fore.RESET}")
                shutil.rmtree(self._build_dir)
                print(f"{Fore.GREEN}Project reset.{Fore.RESET}")

        elif should_clean:
            if os.path.exists(self._build_dir):
                print(f"{Fore.YELLOW}Soft cleaning: Removing object files...{Fore.RESET}")
                try:
                    subprocess.run(["cmake", "--build", self._build_dir, "--target", "clean"], check=True)
                except subprocess.CalledProcessError:
                    print(f"{Fore.RED}Warning: Clean target failed (maybe project not configured).{Fore.RESET}")

    def _build_section(self, params):
        no_build = "--noBuild" in params

        if no_build:
            print(f"{Fore.CYAN}Stop requested: skipping build phase.{Fore.RESET}")
            return

        print(f"{Fore.CYAN}{Style.BRIGHT}--- Starting Build Process ---{Style.RESET_ALL}")

        if not os.path.exists(self._build_dir):
            os.makedirs(self._build_dir)

        try:
            print(f"{Fore.YELLOW}Configuring CMake...{Fore.RESET}")
            subprocess.run(["cmake", "-S", ".", "-B", self._build_dir], check=True)

            print(f"\n{Fore.YELLOW}Compiling...{Fore.RESET}")
            subprocess.run(["cmake", "--build", self._build_dir, "-j"], check=True)

            print(f"\n{Fore.GREEN}{Style.BRIGHT}✔ Build successful!{Style.RESET_ALL}")

        except subprocess.CalledProcessError:
            print(f"\n{Fore.RED}{Style.BRIGHT}✖ Build failed!{Style.RESET_ALL}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"\n{Fore.RED}Error: 'cmake' command not found. Please install CMake.{Fore.RESET}")
            sys.exit(1)

    def get_short_help(self):
        return "Compile the current project using CMake."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm build [options]{Fore.RESET}\n\n"
                "Options:\n"
                "  --clean    : Perform a soft clean (remove objects) before building.\n"
                "  --reset    : Perform a hard clean (delete build folder) before building.\n"
                "  --noBuild  : Stop after the clean/reset phase.\n\n"
                "Example: 'dcpm build --reset --noBuild' to just wipe the build folder.")
