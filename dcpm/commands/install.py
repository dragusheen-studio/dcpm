import os
import shutil
import subprocess
from colorama import Fore, Style
from .base import BaseCommand

class InstallCommand(BaseCommand):
    _modules_dir = ".dcpm/modules"

    def run(self, params):
        if not self.dcpm_validation(): return

        config = self.get_dcpm_config()
        if not config: return

        dependencies = config.get("dependencies", {})
        wanted_libs = set(dependencies.keys())

        if not os.path.exists(self._modules_dir):
            os.makedirs(self._modules_dir)
        
        installed_libs = set(os.listdir(self._modules_dir))

        print(f"{Fore.CYAN}{Style.BRIGHT}--- Synchronizing Dependencies ---{Style.RESET_ALL}")

        to_remove = installed_libs - wanted_libs
        for lib in to_remove:
            self._remove_lib(lib)

        to_install = wanted_libs - installed_libs
        if not to_install and not to_remove:
            print(f"{Fore.GREEN}All dependencies are already up to date.{Fore.RESET}")
            return

        for lib in to_install:
            self._clone_lib(lib, dependencies[lib])

        print(f"\n{Fore.GREEN}{Style.BRIGHT}✔ System synchronized with config.json{Style.RESET_ALL}")

    def _remove_lib(self, name):
        path = os.path.join(self._modules_dir, name)
        print(f"{Fore.YELLOW}Removing unused library: {Fore.RESET}{name}")
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"{Fore.RED}  → Error while removing {name}: {e}{Fore.RESET}")

    def _clone_lib(self, name, info):
        url = info.get("url")
        version = info.get("version")
        dest_path = os.path.join(self._modules_dir, name)

        print(f"{Fore.BLUE}Installing {Style.BRIGHT}{name}{Style.RESET_ALL} ({version})...")
        
        try:
            cmd = ["git", "clone", "--depth", "1"]
            
            if version and version != "default":
                cmd += ["--branch", version]
            
            cmd += [url, dest_path]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"{Fore.GREEN}  → Successfully installed.{Fore.RESET}")
            
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}  → Failed to clone {name}.{Fore.RESET}")
            if e.stderr:
                print(f"{Fore.WHITE}{e.stderr.decode().strip()}{Fore.RESET}")

    def get_short_help(self):
        return "Synchronize installed modules with config.json."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm install{Fore.RESET}\n\n"
                "Synchronizes the '.dcpm/modules/' directory with your configuration:\n"
                "  1. Downloads missing dependencies from Git.\n"
                "  2. Removes unused libraries from the modules folder.\n"
                "  3. Uses shallow cloning (--depth 1) for maximum performance.")
