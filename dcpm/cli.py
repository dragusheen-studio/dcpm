import sys
from colorama import Fore, Style, init
from dcpm.commands import COMMANDS

init(autoreset=True)

def main():
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Erreur: Aucune commande spécifiée.")
        print(f"Utilisez {Fore.CYAN}dcpm help{Fore.RESET} pour voir la liste.")
        sys.exit(1)

    cmd_name = sys.argv[1].lower()
    params = sys.argv[2:]

    if cmd_name in COMMANDS:
        command = COMMANDS[cmd_name]
        command.run(params)
    else:
        print(f"{Fore.RED}Echec: Commande '{cmd_name}' inconnue.")
        print(f"Tapez {Fore.CYAN}dcpm help{Fore.RESET} pour obtenir de l'aide.")
        sys.exit(1)

if __name__ == "__main__":
    main()
