import questionary
import subprocess
import re
import json
import sys
import os
from colorama import Fore, Style
from .base import BaseCommand

class AddCommand(BaseCommand):
    _WHITELIST = {
    }

    def run(self, params):
        if not self.dcpm_validation(): return
        self.current_params = params

        libs_to_add = [p for p in params if not p.startswith("-")]
        if not libs_to_add:
            print(f"{Fore.RED}Error: Missing library name or URL.{Fore.RESET}")
            return

        ask_version = "--version" in params and len(libs_to_add) == 1

        added_libs = []

        for input_source in libs_to_add:
            print(f"\n{Style.BRIGHT}--- Adding: {input_source} ---{Style.RESET_ALL}")

            url = self._WHITELIST.get(input_source, input_source)
            is_external = input_source not in self._WHITELIST

            if is_external:
                if not url.startswith("http") and not url.endswith(".git"):
                    print(f"{Fore.RED}  → Error: Invalid URL format. Skipping.{Fore.RESET}")
                    continue

                confirm = questionary.confirm(f"  External library '{url}'. Proceed?", default=True).ask()
                if confirm is None: self._abort()
                if not confirm: continue

            print(f"{Fore.YELLOW}  Fetching versions...{Fore.RESET}")
            tags = self._fetch_remote_tags(url)

            version = "default"
            if tags:
                if not ask_version:
                    version = tags[0]
                    print(f"{Fore.CYAN}  Using latest version: {Style.BRIGHT}{version}{Style.RESET_ALL}")
                else:
                    choice = questionary.select(
                        f"  Select version for {input_source}:",
                        choices=["latest (branch default)"] + tags
                    ).ask()
                    if choice is None: self._abort()
                    version = tags[0] if choice == "latest (branch default)" else choice

            final_name = input_source
            if is_external:
                suggested_name = url.split("/")[-1].replace(".git", "")
                alias = questionary.text(f"  Enter alias (default: {suggested_name}):").ask()
                if alias is None: self._abort()
                final_name = alias if alias and alias.strip() else suggested_name

            self._save_dependency(final_name, url, version, silent_install=True)
            added_libs.append(final_name)

        if "--noInstall" not in self.current_params:
            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}Triggering global installation...{Style.RESET_ALL}")
            from .install import InstallCommand
            installer = InstallCommand()
            installer.run([])

            config = self.get_dcpm_config()
            updated = False
            for lib in added_libs:
                config, hook_found = self._check_and_configure_library_hooks(lib, config)
                if hook_found:
                    updated = True

            if updated:
                with open(self._config_path, "w") as f:
                    json.dump(config, f, indent=4)
        else:
            print(f"\n{Fore.YELLOW}⚠️  --noInstall used. Hooks validation skipped until next 'dcpm install'.{Fore.RESET}")

    def _fetch_remote_tags(self, url):
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--tags", "--refs", url],
                capture_output=True, text=True, timeout=10
            )
            tags = re.findall(r"refs/tags/(.*)", result.stdout)

            def version_key(v):
                parts = re.split(r'[.-]', v.lstrip('v'))
                return [int(p) if p.isdigit() else p for p in parts]

            try:
                return sorted(tags, key=version_key, reverse=True)
            except Exception:
                return sorted(tags, reverse=True)
        except Exception:
            return []

    def _abort(self):
        print(f"\n{Fore.YELLOW}Operation cancelled by user.{Fore.RESET}")
        sys.exit(0)

    def _save_dependency(self, name, url, version, silent_install=False):
        config = self.get_dcpm_config()
        if not config: return
        if "dependencies" not in config: config["dependencies"] = {}

        config["dependencies"][name] = {"url": url, "version": version}

        with open(self._config_path, "w") as f:
            json.dump(config, f, indent=4)

        print(f"{Fore.GREEN}  ✔ '{name}' ({version}) registered.{Fore.RESET}")

    def _check_and_configure_library_hooks(self, lib_name, main_config):
        lib_config_path = os.path.join(".dcpm", "modules", lib_name, ".dcpm", "config.json")

        if not os.path.exists(lib_config_path):
            return main_config, False

        with open(lib_config_path, "r") as f:
            try:
                lib_config = json.load(f)
            except Exception:
                return main_config, False

        lib_hooks = lib_config.get("hooks", {}).get("pre-build", {})
        if not lib_hooks:
            return main_config, False

        print(f"\n{Fore.YELLOW}⚠️  Dependency '{lib_name}' embedding pre-build integration tasks.{Fore.RESET}")
        if all(not h.get("inputs") for h in lib_hooks.values()):
            print(f"{Fore.GREEN}  ✔ No configuration needed for '{lib_name}' hooks. Skipping mapping.{Fore.RESET}")
            return main_config, True
        print(f"{Fore.WHITE}Please map the required configuration tokens below:{Fore.RESET}")

        if "hooks_mapping" not in main_config:
            main_config["hooks_mapping"] = {}
        if lib_name not in main_config["hooks_mapping"]:
            main_config["hooks_mapping"][lib_name] = {}

        hook_found = False
        for hook_name, hook_data in lib_hooks.items():
            needed_inputs = hook_data.get("inputs", [])

            if needed_inputs:
                hook_found = True
                print(f"\n{Style.BRIGHT}Hook Module: {hook_name}{Style.RESET_ALL}")

                for inp in needed_inputs:
                    val = questionary.text(f"  ? Setup parameter '{inp}':").ask()
                    if val is None: self._abort()
                    main_config["hooks_mapping"][lib_name][inp] = val.strip() if val else ""

        if hook_found:
            print(f"\n{Fore.GREEN}✔ Hook environment variables for '{lib_name}' mapped successfully.{Fore.RESET}\n")

        return main_config, hook_found

    def get_short_help(self):
        return "Add one or more dependencies."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm add <lib1> [lib2]... [flags]{Fore.RESET}\n\n"
                "Flags:\n"
                "  --version   : Manually select version (works only for a single library).\n"
                "  --noInstall : Don't run installation after adding libraries.")
