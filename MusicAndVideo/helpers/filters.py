from typing import List, Union

from pyrogram import filters

from MusicAndVideo.config import COMMAND_PREFIXES

F1 = filters.group & ~filters.edited & ~filters.via_bot & ~filters.forwarded
F2 = ~filters.edited & ~filters.via_bot & ~filters.forwarded


def command(commands: Union[str, List[str]]):
    return filters.command(commands, COMMAND_PREFIXES)
