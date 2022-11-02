import asyncio
import os
import sys
from datetime import datetime
from time import time

from pyrogram import Client, filters

from MusicAndVideo.config import OWNER_ID, bot
from MusicAndVideo.helpers.decorators import owneronly
from MusicAndVideo.helpers.filters import command

START_TIME = datetime.utcnow()
TIME_DURATION_UNITS = (
    ("Minggu", 60 * 60 * 24 * 7),
    ("Hari", 60 * 60 * 24),
    ("Jam", 60 * 60),
    ("Menit", 60),
    ("Detik", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else ""}')
    return ", ".join(parts)


@Client.on_message(command(["ping"]) & ~filters.edited)
async def ping(_, m):
    start = time()
    current_time = datetime.utcnow()
    delta_ping = time() - start
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    A = await bot.get_users(OWNER_ID[0])
    _ping = f"<b>❏ PONG!!🏓\n├• Pinger - `{delta_ping * 1000:.3f} ms`\n├• Aktif - `{uptime}`\n└• Pemilik - {A.mention}</b>"
    await m.reply(_ping)


@Client.on_message(command(["restart"]) & ~filters.edited)
@owneronly
async def restart(_, m):
    await m.delete()
    loli = await m.reply("1")
    await loli.edit("2")
    await loli.edit("3")
    await loli.edit("4")
    await loli.edit("5")
    await loli.edit("6")
    await loli.edit("7")
    await loli.edit("8")
    await loli.edit("9")
    await loli.edit("**✅ Userbot Di Mulai Ulang**")
    await asyncio.sleep(1)
    await loli.delete()
    os.execl(sys.executable, sys.executable, *sys.argv)
    sys.exit()
