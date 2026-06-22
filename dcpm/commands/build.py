import os
import subprocess
import sys
import shutil
import json
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

        config = self.get_dcpm_config()
        if not config: return

        hooks_success = self._execute_all_pre_build_hooks(config)
        if not hooks_success:
            sys.exit(1)

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

    def _execute_all_pre_build_hooks(self, project_config):
        dependencies = project_config.get("dependencies", {})
        hooks_mapping = project_config.get("hooks_mapping", {})

        if not dependencies:
            return True

        has_hooks = False
        for lib_name in dependencies.keys():
            lib_config_path = os.path.join(".dcpm", "modules", lib_name, ".dcpm", "config.json")
            if os.path.exists(lib_config_path):
                with open(lib_config_path, "r") as f:
                    try:
                        lib_cfg = json.load(f)
                        if lib_cfg.get("hooks", {}).get("pre-build"):
                            has_hooks = True
                            break
                    except Exception:
                        continue

        if not has_hooks:
            return True

        print(f"\n{Fore.CYAN}{Style.BRIGHT}--- Checking Dependency Pre-Build Hooks ---{Style.RESET_ALL}")

        for lib_name in dependencies.keys():
            lib_dir = os.path.join(".dcpm", "modules", lib_name)
            lib_config_path = os.path.join(lib_dir, ".dcpm", "config.json")

            if not os.path.exists(lib_config_path):
                continue

            with open(lib_config_path, "r") as f:
                try:
                    lib_config = json.load(f)
                except Exception:
                    continue

            lib_pre_build_hooks = lib_config.get("hooks", {}).get("pre-build", {})
            if not lib_pre_build_hooks:
                continue

            print(f"{Fore.YELLOW}📦 Library '{lib_name}' has tasks to execute:{Fore.RESET}")
            user_inputs = hooks_mapping.get(lib_name, {})

            for hook_name, hook_data in lib_pre_build_hooks.items():
                print(f"  👉 Running {Fore.WHITE}{Style.BRIGHT}[{hook_name}]{Style.RESET_ALL}...")

                success = self._trigger_hook_subprocess(hook_data, lib_path=lib_dir, user_inputs=user_inputs)
                if not success:
                    print(f"{Fore.RED}❌ Error: Pre-build hook '{hook_name}' failed for library '{lib_name}'.{Fore.RESET}")
                    return False

        print(f"{Fore.GREEN}✔ All pre-build tasks completed successfully.{Fore.RESET}\n")
        return True

    def _trigger_hook_subprocess(self, hook_data, lib_path, user_inputs):
        raw_cmd = hook_data.get("cmd")
        actual_cmd_base = raw_cmd.replace("${LIB_PATH}", lib_path)

        args = [
            f"lib_path:{lib_path}",
            f"root_path:{os.getcwd()}",
        ]

        for key, val in user_inputs.items():
            args.append(f"\"{key}:{val}\"")

        final_shell_cmd = f"{actual_cmd_base} {' '.join(args)}"

        try:
            result = subprocess.run(final_shell_cmd, shell=True, cwd=os.getcwd(), check=True)
            return result.returncode == 0
        except Exception:
            return False

    def get_short_help(self):
        return "Compile the current project using CMake."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm build [options]{Fore.RESET}\n\n"
                "Options:\n"
                "  --clean    : Perform a soft clean (remove objects) before building.\n"
                "  --reset    : Perform a hard clean (delete build folder) before building.\n"
                "  --noBuild  : Stop after the clean/reset phase.\n\n"
                "Example: 'dcpm build --reset --noBuild' to just wipe the build folder.")
