"""Small, dependency-free terminal presentation helpers."""

from __future__ import annotations

import os
import shutil
import sys

from lupohack import __version__

_WORDMARK = r"""
 _     _   _ ____   ___  _   _    _    ____ _  __
| |   | | | |  _ \ / _ \| | | |  / \  / ___| |/ /
| |   | | | | |_) | | | | | | | / _ \| |   | ' /
| |___| |_| |  __/| |_| | |_| |/ ___ \| |___| . \
|_____\___/|_|    \___/ \___//_/   \_\____|_|\_\
""".strip("\n").splitlines()

_FOX = r"""
       /\_/\
      /     \
     (  o o  )
      \  ^  /
       /___\
""".strip("\n").splitlines()


def render_banner(*, width: int | None = None, color: bool | None = None) -> str:
    """Render a readable ASCII banner that fits narrow and non-color terminals."""
    terminal_width = width or shutil.get_terminal_size((80, 24)).columns
    if color is None:
        color = (
            bool(getattr(sys.stdout, "isatty", lambda: False)()) and "NO_COLOR" not in os.environ
        )

    red, cyan, reset = ("\033[1;31m", "\033[36m", "\033[0m") if color else ("", "", "")
    if terminal_width >= 62:
        rows = [red + row + reset for row in _WORDMARK]
        rows.extend(
            [
                f"{red}LUPOHACK{reset}",
                "",
                f"{red}{_FOX[0]}{reset}  {cyan}LupoHack {__version__}{reset}",
                f"{red}{_FOX[1]}{reset}  {cyan}Local defensive security toolkit{reset}",
                f"{red}{_FOX[2]}{reset}  Authorized assessment and local analysis{reset}",
                f"{red}{_FOX[3]}{reset}",
                f"{red}{_FOX[4]}{reset}",
                "",
            ]
        )
    else:
        rows = [
            f"{red}{_FOX[0]}{reset}  {red}LUPOHACK{reset} {__version__}",
            f"{red}{_FOX[1]}{reset}  Local defensive security toolkit",
            f"{red}{_FOX[2]}{reset}  Authorized use only",
            f"{red}{_FOX[3]}{reset}",
            f"{red}{_FOX[4]}{reset}",
        ]
    return "\n".join(rows)
