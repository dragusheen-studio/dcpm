import os
import shutil
import subprocess
import json
from colorama import Fore, Style
from .base import BaseCommand

class InstallCommand(BaseCommand):
    _modules_dir = ".dcpm/modules"
    _lock_path = ".dcpm/lock.json"

    def run(self, params):
        if not self.dcpm_validation(): return

        config = self.get_dcpm_config()
        if not config: return

        lock_data = self._get_lock_data()
        
        to_process = config.get("dependencies", {}).copy()
        processed_data = {}
        
        print(f"{Fore.CYAN}{Style.BRIGHT}--- Recursive Installation & Locking ---{Style.RESET_ALL}")

        while to_process:
            alias = list(to_process.keys())[0]
            info = to_process.pop(alias)
            
            if alias in processed_data:
                continue

            locked_commit = lock_data.get(alias, {}).get("commit")
            
            success, final_commit = self._sync_lib(alias, info, locked_commit)
            
            if success:
                processed_data[alias] = {
                    "url": info.get("url"),
                    "version": info.get("version"),
                    "commit": final_commit
                }
                
                sub_deps = self._get_sub_dependencies(alias)
                for sub_alias, sub_info in sub_deps.items():
                    if sub_alias not in processed_data:
                        if sub_alias in to_process:
                            if to_process[sub_alias]['version'] != sub_info['version']:
                                print(f"{Fore.YELLOW}⚠ Version mismatch for {sub_alias}. Using {to_process[sub_alias]['version']}{Fore.RESET}")
                        else:
                            to_process[sub_alias] = sub_info

        self._prune_unused(set(processed_data.keys()))
        self._update_full_cmake(processed_data.keys())
        self._write_lock_file(processed_data)

        print(f"\n{Fore.GREEN}{Style.BRIGHT}✔ System synchronized and locked ({len(processed_data)} modules).{Style.RESET_ALL}")

    def _sync_lib(self, name, info, locked_commit):
        dest_path = os.path.join(self._modules_dir, name)
        url = info.get("url")
        version = info.get("version")

        if not os.path.exists(dest_path):
            print(f"{Fore.BLUE}Installing {Style.BRIGHT}{name}{Style.RESET_ALL}...", end=" ", flush=True)
            try:
                subprocess.run(["git", "clone", url, dest_path], check=True, capture_output=True)
                
                target = locked_commit if locked_commit else version
                if target and target != "default":
                    subprocess.run(["git", "checkout", target], cwd=dest_path, check=True, capture_output=True)
                
                commit = self._get_current_commit(dest_path)
                print(f"{Fore.GREEN}done ({commit[:7]}){Fore.RESET}")
                return True, commit
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}failed{Fore.RESET}")
                return False, None

        current_commit = self._get_current_commit(dest_path)
        if locked_commit and current_commit != locked_commit:
            print(f"{Fore.YELLOW}Syncing {Style.BRIGHT}{name}{Style.RESET_ALL} to locked commit {locked_commit[:7]}...", end=" ", flush=True)
            try:
                subprocess.run(["git", "fetch"], cwd=dest_path, check=True, capture_output=True)
                subprocess.run(["git", "checkout", locked_commit], cwd=dest_path, check=True, capture_output=True)
                print(f"{Fore.GREEN}ok{Fore.RESET}")
                return True, locked_commit
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}error{Fore.RESET}")
                return False, current_commit
        
        return True, current_commit

    def _get_current_commit(self, path):
        try:
            res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except Exception:
            return "unknown"

    def _get_lock_data(self):
        if os.path.exists(self._lock_path):
            try:
                with open(self._lock_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _write_lock_file(self, data):
        os.makedirs(os.path.dirname(self._lock_path), exist_ok=True)
        with open(self._lock_path, "w") as f:
            json.dump(data, f, indent=4)

    def _get_sub_dependencies(self, alias):
        sub_config_path = os.path.join(self._modules_dir, alias, ".dcpm", "config.json")
        if os.path.exists(sub_config_path):
            try:
                with open(sub_config_path, "r") as f:
                    data = json.load(f)
                return data.get("dependencies", {})
            except Exception:
                return {}
        return {}

    def _prune_unused(self, needed_libs):
        if not os.path.exists(self._modules_dir): return
        installed = set(os.listdir(self._modules_dir))
        to_delete = installed - needed_libs
        for folder in to_delete:
            print(f"{Fore.YELLOW}Pruning unused dependency: {folder}{Fore.RESET}")
            shutil.rmtree(os.path.join(self._modules_dir, folder))

    def _update_full_cmake(self, all_libs):
        cmake_path = ".dcpm/dcpm.cmake"
        lines = [
            "# This file is auto-generated by dcpm.",
            "# It includes all direct and indirect dependencies.",
            "\nset(DCPM_LIBRARIES \"\")\n"
        ]
        
        for lib in sorted(all_libs):
            lib_path = f".dcpm/modules/{lib}"
            lines.append(f"if(EXISTS \"${{CMAKE_SOURCE_DIR}}/{lib_path}/CMakeLists.txt\")")
            lines.append(f"    add_subdirectory({lib_path})")
            lines.append(f"    list(APPEND DCPM_LIBRARIES {lib})")
            lines.append("endif()\n")
            
        with open(cmake_path, "w") as f:
            f.write("\n".join(lines))

    def get_short_help(self):
        return "Synchronize modules and lock versions."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm install{Fore.RESET}\n\n"
                "1. Scans dependencies recursively.\n"
                "2. Clones missing libraries or checkouts locked commits from lock.json.\n"
                "3. Generates dcpm.cmake and updates lock.json with current hashes.")
