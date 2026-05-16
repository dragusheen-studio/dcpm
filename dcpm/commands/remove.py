import questionary
import json
import sys
from colorama import Fore, Style
from .base import BaseCommand

class RemoveCommand(BaseCommand):
    def run(self, params):
        self.current_params = params
        if not self.dcpm_validation(): return

        libs_to_remove = [p for p in params if not p.startswith("-")]

        if not libs_to_remove:
            print(f"{Fore.RED}Error: Missing library name(s) to remove.{Fore.RESET}")
            print(f"Usage: {Fore.GREEN}dcpm remove <lib1> [lib2]... [--noInstall]{Fore.RESET}")
            return

        config = self.get_dcpm_config()
        if not config: return

        dependencies = config.get("dependencies", {})
        any_removed = False

        for lib_name in libs_to_remove:
            if lib_name not in dependencies:
                print(f"{Fore.YELLOW}Warning: Library '{lib_name}' not found in configuration. Skipping.{Fore.RESET}")
                continue

            confirm = questionary.confirm(f"Remove '{lib_name}' from project?", default=True).ask()
            if confirm is None: 
                self._abort()
            
            if confirm:
                del config["dependencies"][lib_name]
                print(f"{Fore.GREEN}  ✔ '{lib_name}' marked for removal.{Fore.RESET}")
                any_removed = True

        if any_removed:
            with open(self._config_path, "w") as f:
                json.dump(config, f, indent=4)

            print(f"\n{Fore.BLUE}✔ Project configuration and CMake updated.{Fore.RESET}")

            if "--noInstall" not in self.current_params:
                print(f"{Fore.MAGENTA}{Style.BRIGHT}Synchronizing modules folder...{Style.RESET_ALL}")
                from .install import InstallCommand
                installer = InstallCommand()
                installer.run([])
        else:
            print(f"{Fore.YELLOW}No changes made.{Fore.RESET}")

    def _abort(self):
        print(f"\n{Fore.YELLOW}Operation cancelled by user.{Fore.RESET}")
        sys.exit(0)

    def get_short_help(self):
        return "Remove one or more dependencies."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm remove <lib1> [lib2]... [--noInstall]{Fore.RESET}\n\n"
                "1. Removes specified libraries from config.json.\n"
                "2. Updates dcpm.cmake to unlink them.\n"
                "3. Automatically runs 'dcpm install' to delete physical files unless --noInstall is present.")
