import questionary
import subprocess
import re
import json
import sys
from colorama import Fore, Style
from .base import BaseCommand

class AddCommand(BaseCommand):
    _WHITELIST = {
        "nlohmann_json": "https://github.com/nlohmann/json.git",
        "spdlog": "https://github.com/gabime/spdlog.git",
        "fmt": "https://github.com/fmtlib/fmt.git"
    }

    def run(self, params):
        if not self.dcpm_validation(): return

        self.current_params = params
        if not params or params[0].startswith("-"):
            print(f"{Fore.RED}Error: Missing library name or URL.{Fore.RESET}")
            return

        input_source = params[0]
        use_latest = "--latest" in params
        
        url = self._WHITELIST.get(input_source, input_source)
        is_external = input_source not in self._WHITELIST

        if is_external:
            if not url.startswith("http") and not url.endswith(".git"):
                print(f"{Fore.RED}Error: Invalid URL format.{Fore.RESET}")
                return
            
            confirm = questionary.confirm(f"External library. Proceed?", default=True).ask()
            if confirm is None: self._abort()
            if not confirm: return

        print(f"{Fore.YELLOW}Fetching versions for {url}...{Fore.RESET}")
        tags = self._fetch_remote_tags(url)
        
        version = "default"
        if tags:
            if use_latest:
                version = tags[0]
            else:
                choice = questionary.select(
                    "Select version:",
                    choices=["latest (branch default)"] + tags
                ).ask()
                
                if choice is None: self._abort()
                version = tags[0] if choice == "latest (branch default)" else choice

        final_name = input_source
        if is_external:
            suggested_name = url.split("/")[-1].replace(".git", "")
            alias = questionary.text(f"Enter alias (default: {suggested_name}):").ask()
            if alias is None: self._abort()
            final_name = alias if alias and alias.strip() else suggested_name

        self._save_dependency(final_name, url, version)

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

    def _save_dependency(self, name, url, version):
        config = self.get_dcpm_config()
        if not config: return
        if "dependencies" not in config: config["dependencies"] = {}

        config["dependencies"][name] = {"url": url, "version": version}

        with open(self._config_path, "w") as f:
            json.dump(config, f, indent=4)
        self.update_dcpm_cmake()
        
        print(f"\n{Fore.GREEN}✔ Added '{name}' ({version}) to config.json.{Fore.RESET}")

        if "--noInstall" not in self.current_params:
            from .install import InstallCommand
            installer = InstallCommand()
            installer.run([])

    def get_short_help(self):
        return "Add a dependency (whitelist or URL) to configuration."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm add <name|url> [--latest]{Fore.RESET}\n\n"
                "Updates your config.json with a new dependency. For external URLs,\n"
                "it allows you to define a short alias for easier project management.")
