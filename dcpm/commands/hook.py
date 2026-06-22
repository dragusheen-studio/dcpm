import os
import json
import subprocess
import questionary
from colorama import Fore, Style
from .base import BaseCommand

class HookCommand(BaseCommand):
    def run(self, params):
        if not self.dcpm_validation(): return

        config = self.get_dcpm_config()
        if not config: return

        if not params:
            print(f"{Fore.RED}❌ Error: Missing action argument.{Fore.RESET}")
            print(f"Usage: dcpm hook [add|run|remove]")
            print(f"Run {Fore.YELLOW}dcpm help hook{Fore.RESET} for a detailed guide.")
            return

        action = params[0].lower()

        if action == "add":
            self._manage_wizard(config)
        elif action == "run":
            self._run_manual_hook(config)
        elif action == "remove":
            self._remove_hook(config)
        else:
            print(f"{Fore.RED}❌ Error: Unknown action '{action}'.{Fore.RESET}")
            print(f"Available actions: {Fore.YELLOW}add{Fore.RESET}, {Fore.YELLOW}run{Fore.RESET}, {Fore.YELLOW}remove{Fore.RESET}")

    def _manage_wizard(self, config):
        print(f"{Fore.CYAN}{Style.BRIGHT}--- DCPM Hook Configuration Wizard ---{Style.RESET_ALL}\n")

        hook_type = questionary.select(
            "Which type of hook do you want to manage?",
            choices=[
                questionary.Choice("Pre-Build Hook (Runs before CMake compilation)", value="pre-build"),
            ]
        ).ask()

        if not hook_type: return

        existing_hooks = config.get("hooks", {}).get(hook_type, {})

        while True:
            hook_name = questionary.text("Enter a unique name for this hook (e.g., 'ProtocolGen'):").ask()
            if not hook_name:
                print(f"{Fore.RED}❌ Error: Hook name cannot be empty.{Fore.RESET}")
                continue

            hook_name = hook_name.strip()

            if hook_name in existing_hooks:
                print(f"{Fore.YELLOW}⚠️ Warning: A hook named '{hook_name}' already exists in this section. Please choose another name.{Fore.RESET}")
                continue

            break

        if hook_type == "pre-build":
            self._manage_pre_build_hook(config, hook_name)

    def _manage_pre_build_hook(self, config, hook_name):
        exec_type = questionary.select(
            f"How should the hook '{hook_name}' be executed?",
            choices=[
                questionary.Choice("Python Script (Recommended - Generates a starting template)", value="python"),
                questionary.Choice("Custom Command (Run a raw CLI line)", value="custom")
            ]
        ).ask()

        if not exec_type: return

        hook_cmd = ""
        hooks_dir = os.path.join(".dcpm", "hooks", "pre-build")
        inputs = []

        print(f"\n{Fore.WHITE}--- Configure Required Inputs for '{hook_name}' ---{Fore.RESET}")

        while True:
            add_input = questionary.confirm("Do you want to add a required input parameter for the users?", default=False).ask()
            if not add_input:
                break

            input_name = questionary.text("Enter parameter name (e.g., 'config_file'):").ask()
            if not input_name:
                print(f"{Fore.RED}❌ Error: Parameter name cannot be empty.{Fore.RESET}")
                continue

            input_name = input_name.strip()

            if input_name in ["lib_path", "root_path"]:
                print(f"{Fore.YELLOW}⚠️ Warning: '{input_name}' is a reserved internal DCPM keyword. Please use another name.{Fore.RESET}")
                continue

            if input_name in inputs:
                print(f"{Fore.YELLOW}⚠️ Warning: A parameter named '{input_name}' has already been added to this hook. Please use another name.{Fore.RESET}")
                continue

            inputs.append(input_name)
            print(f"{Fore.GREEN}✔ Parameter '{input_name}' registered.{Fore.RESET}")

        if exec_type == "python":
            os.makedirs(hooks_dir, exist_ok=True)
            script_path = os.path.join(hooks_dir, f"{hook_name}.py")

            success = self._generate_dynamic_template(script_path, inputs)
            if not success: return

            hook_cmd = "python3 ${LIB_PATH}/" + script_path
        else:
            hook_cmd = questionary.text("Enter your custom command line (e.g., 'bash scripts/gen.sh'):").ask()
            if not hook_cmd: return

        if "hooks" not in config:
            config["hooks"] = {}
        if "pre-build" not in config["hooks"]:
            config["hooks"]["pre-build"] = {}

        config["hooks"]["pre-build"][hook_name] = {
            "cmd": hook_cmd,
            "inputs": inputs
        }

        with open(".dcpm/config.json", "w") as f:
            json.dump(config, f, indent=4)

        print(f"\n{Fore.GREEN}{Style.BRIGHT}✔ Pre-build hook '{hook_name}' successfully registered!{Style.RESET_ALL}")
        print(f"💡 You can test it right now by running: {Fore.YELLOW}dcpm hook run{Fore.RESET}")

    def _run_manual_hook(self, config):
        print(f"{Fore.CYAN}{Style.BRIGHT}--- DCPM Hook Manual Execution ---{Style.RESET_ALL}\n")

        hooks_config = config.get("hooks", {})
        pre_build_hooks = hooks_config.get("pre-build", {})

        if not pre_build_hooks:
            print(f"{Fore.RED}❌ No hooks registered in this project's .dcpm/config.json.{Fore.RESET}")
            return

        target_type = questionary.select(
            "Which hook section do you want to browse?",
            choices=[
                questionary.Choice("Pre-Build Hooks", value="pre-build"),
            ]
        ).ask()

        if target_type == "pre-build":
            choices = [questionary.Choice(f"🚀 [Run All Pre-Build Hooks]", value="all")]
            for name in pre_build_hooks.keys():
                choices.append(questionary.Choice(f"📦 Run: {name}", value=name))

            chosen_hook = questionary.select("Select the hook to execute:", choices=choices).ask()
            if not chosen_hook: return

            if chosen_hook == "all":
                print(f"{Fore.YELLOW}⚙️ Executing all pre-build hooks sequentially...{Fore.RESET}\n")
                for name, data in pre_build_hooks.items():
                    print(f"{Fore.WHITE}{Style.BRIGHT}👉 [{name}]{Style.RESET_ALL}")
                    user_inputs = self._ask_inputs_for_run(name, data)
                    self.execute_hook_process(data, lib_path=".", user_inputs=user_inputs)
            else:
                data = pre_build_hooks[chosen_hook]
                user_inputs = self._ask_inputs_for_run(chosen_hook, data)
                success = self.execute_hook_process(data, lib_path=".", user_inputs=user_inputs)
                if success:
                    print(f"\n{Fore.GREEN}{Style.BRIGHT}✔ Hook '{chosen_hook}' executed successfully!{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}{Style.BRIGHT}❌ Hook '{chosen_hook}' execution failed.{Style.RESET_ALL}")

    def _remove_hook(self, config):
        print(f"{Fore.CYAN}{Style.BRIGHT}--- DCPM Hook Deletion Wizard ---{Style.RESET_ALL}\n")

        hooks_config = config.get("hooks", {})
        pre_build_hooks = hooks_config.get("pre-build", {})

        if not pre_build_hooks:
            print(f"{Fore.RED}❌ No hooks found to delete in .dcpm/config.json.{Fore.RESET}")
            return

        target_type = questionary.select(
            "From which section do you want to remove hooks?",
            choices=[
                questionary.Choice("Pre-Build Hooks", value="pre-build"),
            ]
        ).ask()

        if target_type == "pre-build":
            choices = [questionary.Choice(f"🚨 [Delete All Pre-Build Hooks]", value="all")]
            for name in pre_build_hooks.keys():
                choices.append(questionary.Choice(f"🗑️ Remove: {name}", value=name))

            chosen_hook = questionary.select("Select the hook to remove:", choices=choices).ask()
            if not chosen_hook: return

            confirm = questionary.confirm(f"Are you sure you want to delete '{chosen_hook}'? This action cannot be undone.", default=False).ask()
            if not confirm: return

            if chosen_hook == "all":
                for name in list(pre_build_hooks.keys()):
                    self._delete_hook_files_and_config(config, "pre-build", name)
            else:
                self._delete_hook_files_and_config(config, "pre-build", chosen_hook)

            with open(".dcpm/config.json", "w") as f:
                json.dump(config, f, indent=4)

            print(f"\n{Fore.GREEN}{Style.BRIGHT}✔ Deletion process completed and manifest updated!{Style.RESET_ALL}")

    def _delete_hook_files_and_config(self, config, hook_type, hook_name):
        hook_data = config["hooks"][hook_type][hook_name]
        cmd = hook_data.get("cmd", "")

        if "python3 ${LIB_PATH}/" in cmd:
            relative_script_path = cmd.replace("python3 ${LIB_PATH}/", "")
            if os.path.exists(relative_script_path):
                try:
                    os.remove(relative_script_path)
                    print(f"{Fore.GREEN}✔ Removed script file:{Fore.RESET} {relative_script_path}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Failed to delete file {relative_script_path}: {e}{Fore.RESET}")

        del config["hooks"][hook_type][hook_name]
        print(f"{Fore.GREEN}✔ Removed entry '{hook_name}' from manifest.{Fore.RESET}")

        if not config["hooks"][hook_type]:
            del config["hooks"][hook_type]
        if not config["hooks"]:
            del config["hooks"]

    def _ask_inputs_for_run(self, name, hook_data):
        user_inputs = {}
        if hook_data.get("inputs"):
            print(f"{Fore.YELLOW}📋 '{name}' requires parameters. Please fill them in:{Fore.RESET}")
            for inp in hook_data.get("inputs", []):
                val = questionary.text(f"Value for '{inp}':").ask()
                user_inputs[inp] = val if val else ""
            print("")
        return user_inputs

    def execute_hook_process(self, hook_data, lib_path, user_inputs):
        raw_cmd = hook_data.get("cmd")
        actual_cmd_base = raw_cmd.replace("${LIB_PATH}", lib_path)

        args = [
            f"lib_path:{lib_path}",
            f"root_path:."
        ]

        for key, val in user_inputs.items():
            args.append(f"{key}:{val}")

        final_shell_cmd = f"{actual_cmd_base} {' '.join(args)}"

        print(f"{Fore.BLUE}🚀 Executing:{Fore.RESET} {Fore.WHITE}{final_shell_cmd}{Fore.RESET}\n")

        try:
            result = subprocess.run(final_shell_cmd, shell=True, cwd=".", check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"\n{Fore.RED}❌ Process crashed with exit code {e.returncode}{Fore.RESET}\n")
            return False
        except Exception as e:
            print(f"\n{Fore.RED}❌ Failed to execute subprocess: {e}{Fore.RESET}\n")
            return False

    def _generate_dynamic_template(self, dest_path, custom_inputs):
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_source = os.path.join(current_dir, "templates", "hook", "pre-build-hook.template")

        if not os.path.exists(template_source):
            print(f"{Fore.RED}❌ Error: Core template not found at {template_source}{Fore.RESET}")
            return False

        try:
            with open(template_source, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                new_lines.append(line)
                if 'root_path = args.get("root_path", ".")' in line:
                    for inp in custom_inputs:
                        new_lines.append(f'    {inp} = args.get("{inp}", "")\n')
                        new_lines.append(f'    print(f"[DCPM Hook] Custom parameter {inp}: {{{inp}}}")\n')

            with open(dest_path, "w") as f:
                f.writelines(new_lines)

            print(f"{Fore.GREEN}✔ Dynamic Python template generated at: {dest_path}{Fore.RESET}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating dynamic template: {e}{Fore.RESET}")
            return False

    def get_short_help(self):
        return "Manage project and library hooks dynamically."

    def get_long_help(self):
        return (
            f"{Style.BRIGHT}DCPM HOOK SYSTEM MANAGEMENT (MULTI-HOOK SUPPORT){Style.RESET_ALL}\n"
            f"========================================================\n"
            f"The `{Fore.GREEN}hook{Fore.RESET}` command allows package creators to embed multiple custom automation tasks\n"
            f"isolated by unique names under specific build phases.\n\n"
            f"{Style.BRIGHT}SYNTAX{Style.RESET_ALL}\n"
            f"  {Fore.GREEN}dcpm hook add{Fore.RESET}    : Launches the multi-step interactive wizard to create a new named hook.\n"
            f"  {Fore.GREEN}dcpm hook run{Fore.RESET}    : Launches the interactive runner to test a specific hook or all of them.\n"
            f"  {Fore.GREEN}dcpm hook remove{Fore.RESET} : Launches the deletion tool to cleanly purge script assets and configurations.\n\n"
            f"{Style.BRIGHT}ENVIRONMENT VARIABLES INJECTED AUTOMATICALLY{Style.RESET_ALL}\n"
            f"  Every hook script executed by DCPM implicitly receives two key contextual variables:\n"
            f"    • {Fore.CYAN}lib_path{Fore.RESET}  : Path to the root directory where the executed library code sits.\n"
            f"    • {Fore.CYAN}root_path{Fore.RESET} : Path to the main project directory initiating the build pipeline.\n"
        )
