from .init import InitCommand
from .add import AddCommand
from .install import InstallCommand
from .run import RunCommand
from .help import HelpCommand
from .build import BuildCommand
from .remove import RemoveCommand
from .update import UpdateCommand

COMMANDS = {
    "init": InitCommand(),
    "add": AddCommand(),
	"remove": RemoveCommand(),
    "install": InstallCommand(),
	"update": UpdateCommand(),
    "run": RunCommand(),
	"build": BuildCommand(),
    "help": HelpCommand()
}
