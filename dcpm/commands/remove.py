import questionary
import json
from colorama import Fore, Style
from .base import BaseCommand

class RemoveCommand(BaseCommand):
    def run(self, params):
        if not self.dcpm_validation():  return

        self.current_params = params
        if not params:
            print(f"{Fore.RED}Error: Missing library name to remove.{Fore.RESET}")
            print(f"Usage: {Fore.GREEN}dcpm remove <alias>{Fore.RESET}")
            return

        lib_name = params[0]
        config = self.get_dcpm_config()
        
        if not config or "dependencies" not in config or lib_name not in config["dependencies"]:
            print(f"{Fore.RED}Error: Library '{lib_name}' not found in configuration.{Fore.RESET}")
            return

        confirm = questionary.confirm(f"Are you sure you want to remove '{lib_name}' from the project?", default=True).ask()
        if confirm is None:
            print(f"\n{Fore.YELLOW}Operation cancelled.{Fore.RESET}")
            return
        
        if not confirm:
            return

        del config["dependencies"][lib_name]

        with open(self._config_path, "w") as f:
            json.dump(config, f, indent=4)
        
        print(f"{Fore.GREEN}✔ Removed '{lib_name}' from config.json.{Fore.RESET}")

        self.update_dcpm_cmake()

        if "--noInstall" not in self.current_params:
            from .install import InstallCommand
            installer = InstallCommand()
            installer.run([])

    def get_short_help(self):
        return "Remove a dependency from the project."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm remove <alias>{Fore.RESET}\n\n"
                "1. Removes the library from config.json.\n"
                "2. Updates dcpm.cmake to unlink the library.\n"
                "3. You must run 'dcpm install' afterwards to delete the files.")
