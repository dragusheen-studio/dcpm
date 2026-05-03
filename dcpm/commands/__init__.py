from .init import InitCommand
from .add import AddCommand
from .install import InstallCommand
from .run import RunCommand
from .help import HelpCommand

# Le registre : facile d'ajouter une commande ici
COMMANDS = {
    "init": InitCommand(),
    "add": AddCommand(),
    "install": InstallCommand(),
    "run": RunCommand(),
    "help": HelpCommand()
}