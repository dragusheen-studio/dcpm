from .add import AddCommand
from .build import BuildCommand
from .help import HelpCommand
from .hook import HookCommand
from .info import InfoCommand
from .init import InitCommand
from .install import InstallCommand
from .remove import RemoveCommand
from .run import RunCommand
from .update import UpdateCommand

COMMANDS = {
    "add": AddCommand(),
	"build": BuildCommand(),
    "help": HelpCommand(),
	"hook": HookCommand(),
	"info": InfoCommand(),
    "init": InitCommand(),
    "install": InstallCommand(),
	"remove": RemoveCommand(),
    "run": RunCommand(),
	"update": UpdateCommand(),
}
