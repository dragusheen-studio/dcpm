import questionary
import os
import json
import re
from colorama import Fore, Style
from .base import BaseCommand
from dcpm.utils.text import to_snake_case

class InitCommand(BaseCommand):
    def run(self, params):
        raw_path = params[0] if params else None
        
        if not raw_path:
            target_dir = None 
            default_project_name = "new_cpp_project"
        elif raw_path == ".":
            target_dir = os.getcwd()
            default_project_name = os.path.basename(target_dir)
        else:
            target_dir = os.path.abspath(raw_path)
            default_project_name = os.path.basename(target_dir)

        answers = self._get_form_response(default_project_name)
        if not answers: return

        if target_dir is None:
            target_dir = os.path.abspath(answers['name'])
        
        os.makedirs(target_dir, exist_ok=True)
        self._create_directories(target_dir, answers)
        self._generate_files(target_dir, answers)
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🚀 Project '{answers['name']}' is ready!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Location: {target_dir}{Fore.RESET}")
        print(f"{Fore.YELLOW}Next step: Run {Style.BRIGHT}dcpm install{Style.RESET_ALL}{Fore.YELLOW} to generate your CMake environment.{Fore.RESET}")

    def _create_directories(self, root, answers):
        folders = [
            os.path.join(root, ".dcpm", "modules"),
            os.path.join(root, answers['folders']['sources']),
            os.path.join(root, answers['folders']['includes']),
        ]
        
        if answers['folders'].get('tests'):
            folders.append(os.path.join(root, answers['folders']['tests']))

        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            print(f"{Fore.BLUE}Creating directory:{Fore.RESET} {folder}")

    def _generate_files(self, root, answers):
        config_path = os.path.join(root, ".dcpm", "config.json")
        with open(config_path, 'w') as f:
            json.dump(answers, f, indent=4)
        
        if hasattr(self, '_setup_options') and self._setup_options.get('clang_style'):
            style = self._setup_options['clang_style']
            content = f"BasedOnStyle: {style}" if style != "Empty (Custom)" else "# Add your custom rules here"
            with open(os.path.join(root, ".clang-format"), 'w') as f:
                f.write(content)

        keys = {
            "PROJECT_NAME": answers['name'],
            "PROJECT_PASCAL": answers['name'],
            "NAMESPACE": to_snake_case(answers['name']),
            "CPP_STD": answers['cpp_std'],
            "SRC_DIR": answers['folders']['sources'],
            "INCLUDE_DIR": answers['folders']['includes'],
            "TEST_DIR": answers['folders'].get('tests'),
            "LIB_TYPE": (answers.get('lib_type') or "STATIC").upper()
        }

        type_map = {
            "Executable": "executable",
            "Library": "library",
            "Header-only": "header-only"
        }

        template_folder = type_map[answers['target_type']]
        self._deploy_templates(root, template_folder, keys)

    def _deploy_templates(self, root, template_type, keys):
        mapping = {}
        if hasattr(self, '_setup_options') and self._setup_options.get('use_gitignore'):
            mapping["common/gitignore.template"] = ".gitignore"
        
        if template_type == "executable":
            mapping.update({
                "executable/CMakeLists.txt.template": "CMakeLists.txt",
                "executable/main.cpp.template": f"{keys['SRC_DIR']}/main.cpp",
                "executable/lib.hpp.template": f"{keys['INCLUDE_DIR']}/{keys['PROJECT_PASCAL']}.hpp",
                "executable/lib.cpp.template": f"{keys['SRC_DIR']}/{keys['PROJECT_PASCAL']}.cpp"
            })
            if keys.get("TEST_DIR"):
                mapping["common/test_sample.cpp.template"] = f"{keys['TEST_DIR']}/sample_test.cpp"

        elif template_type == "library":
            mapping.update({
                "library/CMakeLists.txt.template": "CMakeLists.txt",
                "library/lib.hpp.template": f"{keys['INCLUDE_DIR']}/{keys['PROJECT_PASCAL']}.hpp",
                "library/lib.cpp.template": f"{keys['SRC_DIR']}/{keys['PROJECT_PASCAL']}.cpp",
                "library/manual_test.cpp.template": f"{keys['TEST_DIR']}/manual_test.cpp",
                "library/unit_tests.cpp.template": f"{keys['TEST_DIR']}/unit_tests.cpp"
            })

        elif template_type == "header-only":
            mapping.update({
                "header-only/CMakeLists.txt.template": "CMakeLists.txt",
                "header-only/lib.hpp.template": f"{keys['INCLUDE_DIR']}/{keys['PROJECT_PASCAL']}.hpp",
                "library/manual_test.cpp.template": f"{keys['TEST_DIR']}/manual_test.cpp",
                "library/unit_tests.cpp.template": f"{keys['TEST_DIR']}/unit_tests.cpp"
            })

        for src, dest in mapping.items():
            os.makedirs(os.path.dirname(os.path.join(root, dest)), exist_ok=True)
            self._write_template(src, os.path.join(root, dest), keys)

    def _write_template(self, template_path, dest_path, keys):
        template_full_path = os.path.join(os.path.dirname(__file__), "..", "templates", template_path)
        
        with open(template_full_path, 'r') as f:
            content = f.read()
        
        if "${TEST_DIR}" in content and keys.get("TEST_DIR") is None:
            content = re.sub(r'# \[TESTS_SECTION_START\].*?# \[TESTS_SECTION_END\]', '', content, flags=re.DOTALL)
        
        for key, value in keys.items():
            actual_value = str(value) if value is not None else ""
            content = content.replace(f"${{{key}}}", actual_value)
        
        with open(dest_path, 'w') as f:
            f.write(content)

    def _get_form_response(self, default_name):
        print(f"{Fore.CYAN}{Style.BRIGHT}--- DCPM Project Wizard ---{Style.RESET_ALL}\n")

        name = questionary.text("Project Name:", default=default_name).ask()
        if not name: return None

        target_type = questionary.select(
            "Target type:",
            choices=["Executable", "Library", "Header-only"]
        ).ask()
        
        lib_type = None
        if target_type == "Library":
            lib_type = questionary.select("Library Type:", choices=["Static", "Shared"]).ask()

        cpp_std = questionary.select("C++ Standard:", choices=["11", "14", "17", "20", "23"], default="17").ask()
        src_dir = questionary.text("Source directory:", default="src").ask()
        inc_dir = questionary.text("Include directory:", default="include").ask()
        
        test_dir = None
        if target_type in ["Library", "Header-only"]:
            test_dir = questionary.text("Tests directory:", default="tests").ask()
        else:
            use_tests = questionary.confirm("Add unit tests?", default=True).ask()
            if use_tests:
                test_dir = questionary.text("Tests directory:", default="tests").ask()

        use_clang = questionary.confirm("Add .clang-format?", default=True).ask()
        clang_style = None
        if use_clang:
            clang_style = questionary.select("Clang-Format style:", 
                choices=["LLVM", "Google", "Chromium", "Mozilla", "WebKit", "Empty (Custom)"]).ask()

        use_gitignore = questionary.confirm("Add default .gitignore?", default=True).ask()

        self._setup_options = {
            'clang_style': clang_style,
            'use_gitignore': use_gitignore
        }

        print(f"\n{Fore.GREEN}{Style.BRIGHT}Wizard completed!{Style.RESET_ALL}")

        return {
            "name": name,
            "target_type": target_type,
            "cpp_std": cpp_std,
            "lib_type": lib_type,
            "folders": {
                "sources": src_dir,
                "includes": inc_dir,
                "tests": test_dir
            },
            "dependencies": {}
        }

    def get_short_help(self):
        return "Initialize a new C++ project."

    def get_long_help(self):
        return (f"Usage: {Fore.GREEN}dcpm init [project_name]{Fore.RESET}\n\n"
                "Starts an interactive wizard to set up your project structure.\n"
                "Configurable options:\n"
                "  - Target type (Executable or Library)\n"
                "  - C++ Standard (11, 14, 17, 20, 23)\n"
                "  - Source, Header and Test directory naming\n"
                "  - Unit Testing support and Clang-format setup")
