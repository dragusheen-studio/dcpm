import questionary
import json
import os
import sys
import subprocess
import re
from colorama import Fore, Style
from .base import BaseCommand
from .install import InstallCommand

class UpdateCommand(BaseCommand):
    def run(self, params):
        self.current_params = params
        if not self.dcpm_validation(): return

        config = self.get_dcpm_config()
        if not config or "dependencies" not in config or not config["dependencies"]:
            print(f"{Fore.YELLOW}No dependencies to update.{Fore.RESET}")
            return

        target_lib = next((p for p in params if not p.startswith("-")), None)
        show_only = "--list" in params
        force_latest = "--latest" in params
        manual_version = "--version" in params

        libs_to_process = {}
        if target_lib:
            if target_lib not in config["dependencies"]:
                print(f"{Fore.RED}Error: Library '{target_lib}' not found.{Fore.RESET}")
                return
            libs_to_process[target_lib] = config["dependencies"][target_lib]
        else:
            libs_to_process = config["dependencies"]

        updates_available = []
        print(f"{Fore.CYAN}{Style.BRIGHT}--- Checking for updates ---{Style.RESET_ALL}")

        for name, info in libs_to_process.items():
            current_v = info.get("version", "default")
            url = info.get("url")

            print(f"  Checking {Fore.BLUE}{name}{Fore.RESET}...")
            tags = self._fetch_remote_tags(url)

            if not tags:
                continue

            latest_v = tags[0]
            if latest_v != current_v or manual_version:
                updates_available.append({
                    "name": name,
                    "current": current_v,
                    "latest": latest_v,
                    "all_tags": tags,
                    "url": url
                })

        if not updates_available:
            print(f"\n{Fore.GREEN}All libraries are up to date!{Fore.RESET}")
            return

        print(f"\n{Style.BRIGHT}{'LIBRARY':<20} {'CURRENT':<15} {'LATEST':<15}{Style.RESET_ALL}")
        for up in updates_available:
            color = Fore.GREEN if up["current"] != up["latest"] else Fore.WHITE
            print(f"{up['name']:<20} {up['current']:<15} {color}{up['latest']:<15}{Fore.RESET}")

        if show_only:
            return

        any_changed = False
        for up in updates_available:
            perform_update = False
            new_version = up["latest"]

            if force_latest:
                perform_update = True
            elif manual_version and target_lib:
                choice = questionary.select(f"Select version for {up['name']}:", choices=up["all_tags"]).ask()
                if choice is None: self._abort()
                new_version = choice
                perform_update = True
            else:
                msg = f"Update '{up['name']}' to {new_version}?"
                if up["current"] == up["latest"]: msg = f"Reinstall '{up['name']}' ({up['current']})?"
                perform_update = questionary.confirm(msg, default=True).ask()
                if perform_update is None: self._abort()

            if perform_update:
                config["dependencies"][up["name"]]["version"] = new_version
                module_path = os.path.join(".dcpm/modules", up["name"])
                if os.path.exists(module_path):
                    import shutil
                    shutil.rmtree(module_path)

                print(f"{Fore.GREEN}  ✔ {up['name']} updated to {new_version}{Fore.RESET}")
                any_changed = True

        if any_changed:
            with open(self._config_path, "w") as f:
                json.dump(config, f, indent=4)

            print(f"\n{Fore.MAGENTA}Synchronizing modules...{Fore.RESET}")
            installer = InstallCommand()
            installer.run([])

    def _fetch_remote_tags(self, url):
        try:
            result = subprocess.run(["git", "ls-remote", "--tags", "--refs", url], capture_output=True, text=True, timeout=10)
            tags = re.findall(r"refs/tags/(.*)", result.stdout)
            def version_key(v):
                parts = re.split(r'[.-]', v.lstrip('v'))
                return [int(p) if p.isdigit() else p for p in parts]
            return sorted(tags, key=version_key, reverse=True)
        except Exception:
            return []

    def _abort(self):
        print(f"\n{Fore.YELLOW}Update cancelled.{Fore.RESET}")
        sys.exit(0)

    def get_short_help(self):
        return "Check and install updates for dependencies."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm update [lib] [flags]{Fore.RESET}\n\n"
                "Flags:\n"
                "  --list    : Only show available updates without installing.\n"
                "  --latest  : Automatically update to the latest version.\n"
                "  --version : (Single lib only) Choose a specific version to install.")
