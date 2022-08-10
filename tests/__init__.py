import __main__ # type: ignore

from ansible.utils.display import Display
__main__.display = Display()

from suitable.api import Api  # noqa
from suitable.utils import install_strategy_plugins  # noqa

__all__ = ('Api', 'install_strategy_plugins')
