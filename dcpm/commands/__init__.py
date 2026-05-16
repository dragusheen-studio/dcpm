from .init import InitCommand
from .add import AddCommand
from .install import InstallCommand
from .run import RunCommand
from .help import HelpCommand
from .build import BuildCommand
from .remove import RemoveCommand
from .update import UpdateCommand
from .info import InfoCommand


COMMANDS = {
    "init": InitCommand(),
    "add": AddCommand(),
	"remove": RemoveCommand(),
    "install": InstallCommand(),
	"update": UpdateCommand(),
    "run": RunCommand(),
	"info": InfoCommand(),
	"build": BuildCommand(),
    "help": HelpCommand()
}
