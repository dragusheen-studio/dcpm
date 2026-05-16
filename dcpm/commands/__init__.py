from .init import InitCommand
from .add import AddCommand
from .install import InstallCommand
from .run import RunCommand
from .help import HelpCommand
from .build import BuildCommand

COMMANDS = {
    "init": InitCommand(),
    "add": AddCommand(),
    "install": InstallCommand(),
    "run": RunCommand(),
	"build": BuildCommand(),
    "help": HelpCommand()
}
