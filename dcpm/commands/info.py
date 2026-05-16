import os
import json
from colorama import Fore, Style
from .base import BaseCommand

class InfoCommand(BaseCommand):
    def run(self, params):
        if not self.dcpm_validation(): return

        config = self.get_dcpm_config()
        if not config: return

        show_all = len([p for p in params if p.startswith("--")]) == 0
        show_project = show_all or "--project" in params
        show_deps = show_all or "--dependencies" in params

        if show_project:
            self._display_project_info(config)

        if show_deps:
            self._display_dependencies_info(config)

    def _display_project_info(self, config):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== PROJECT INFORMATION ==={Style.RESET_ALL}")
        print(f"{Fore.WHITE}Name        :{Fore.RESET} {config.get('name', 'Unknown')}")
        print(f"{Fore.WHITE}Type        :{Fore.RESET} {config.get('type', 'Unknown')}")
        print(f"{Fore.WHITE}C++ Standard:{Fore.RESET} {config.get('cpp_version', 'Unknown')}")
        
        print(f"{Fore.WHITE}Location    :{Fore.RESET} {os.getcwd()}")
        print("-" * 30)

    def _display_dependencies_info(self, config):
        dependencies = config.get("dependencies", {})
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}=== DEPENDENCIES ==={Style.RESET_ALL}")
        
        if not dependencies:
            print(f"{Fore.YELLOW}No dependencies registered.{Fore.RESET}")
            return

        print(f"{Style.BRIGHT}{'NAME':<20} {'VERSION':<15} {'SIZE':<12} {'URL'}{Style.RESET_ALL}")
        print("-" * 70)

        total_size = 0
        for name, info in dependencies.items():
            url = info.get("url", "N/A")
            version = info.get("version", "N/A")
            
            size_str, size_bytes = self._get_dir_size(f".dcpm/modules/{name}")
            total_size += size_bytes
            
            print(f"{Fore.BLUE}{name:<20}{Fore.RESET} {version:<15} {size_str:<12} {Fore.LIGHTBLACK_EX}{url}{Fore.RESET}")

        print("-" * 70)
        total_str = self._format_size(total_size)
        print(f"{Style.BRIGHT}Total dependencies size: {Fore.GREEN}{total_str}{Style.RESET_ALL}")

    def _get_dir_size(self, path):
        total = 0
        if not os.path.exists(path):
            return "Not installed", 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total += os.path.getsize(fp)
            return self._format_size(total), total
        except Exception:
            return "Error", 0

    def _format_size(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"

    def get_short_help(self):
        return "Display project and dependencies information."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm info [flags]{Fore.RESET}\n\n"
                "Flags:\n"
                "  --project      : Show only project metadata.\n"
                "  --dependencies : Show only details about dependencies.")
