from .init import InitCommand
from .add import AddCommand
from .install import InstallCommand
from .run import RunCommand
from .help import HelpCommand
from .build import BuildCommand
from .remove import RemoveCommand


COMMANDS = {
    "init": InitCommand(),
    "add": AddCommand(),
	"remove": RemoveCommand(),
    "install": InstallCommand(),
    "run": RunCommand(),
	"build": BuildCommand(),
    "help": HelpCommand()
}
