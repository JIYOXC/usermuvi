# Copyright (c) @TheHamkerCat
import sys
import traceback
from functools import wraps
from io import BytesIO
from traceback import format_exc

import aiohttp
from pyrogram import Client
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from Python_ARQ import ARQ

from MusicAndVideo.config import bot
from MusicAndVideo.helpers.filters import command

aiohttpsession = aiohttp.ClientSession()
arq = ARQ("arq.hamker.dev", "ZCHJFR-MWTULN-FVQPSZ-YNIABJ-ARQ", aiohttpsession)


def split_limits(text):
    if len(text) < 2048:
        return [text]
    lines = text.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 2048:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    result.append(small_msg)
    return result


def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            await client.send_message(message.chat.id, "error")
            return
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            error_feedback = split_limits(
                "**ERROR** | `{}` | `{}`\n\n```{}```\n\n```{}```\n".format(
                    message.from_user.id if message.from_user else 0,
                    message.chat.id if message.chat else 0,
                    message.text or message.caption,
                    "".join(errors),
                )
            )
            for x in error_feedback:
                await client.send_message(message.chat.id, x)
            raise err

    return capture


async def quotify(messages: list):
    response = await arq.quotly(messages)
    if not response.ok:
        return [False, response.result]
    sticker = response.result
    sticker = BytesIO(sticker)
    sticker.name = "sticker.webp"
    return [True, sticker]


def getArg(message) -> str:
    return message.text.strip().split(None, 1)[1].strip()


def isArgInt(message) -> bool:
    count = getArg(message)
    try:
        count = int(count)
        return [True, count]
    except ValueError:
        return [False, 0]


@Client.on_message(command(["q"]))
@capture_err
async def quotly_func(client, message):
    if not message.reply_to_message:
        return await message.reply_text("Membalas Pesan Untuk Mengutipnya !")
    m = await message.reply_text("`Membuat kutipan Pesan...`")
    if len(message.command) < 2:
        messages = [message.reply_to_message]
    elif len(message.command) == 2:
        arg = isArgInt(message)
        if arg[0]:
            if arg[1] < 2 or arg[1] > 10:
                return await m.edit("Argumen harus antara 2-10.")
            count = arg[1]
            messages = await client.get_messages(
                message.chat.id,
                list(
                    range(
                        message.reply_to_message.message_id,
                        message.reply_to_message.message_id + count,
                    )
                ),
                replies=0,
            )
        else:
            if getArg(message) != "r":
                return await m.edit("**SORRY**`")
            reply_message = await bot.get_messages(
                message.chat.id,
                message.reply_to_message.message_id,
                replies=1,
            )
            messages = [reply_message]
    else:
        await m.edit("**ERROR**")
        return
    try:
        sticker = await quotify(messages)
        if not sticker[0]:
            await message.reply_text(sticker[1])
            return await m.delete()
        sticker = sticker[1]
        await message.reply_sticker(sticker)
        await m.delete()
        sticker.close()
    except Exception as e:
        await m.edit(
            "Ada yang salah saat mengutip pesan, bisa"
            + " Kesalahan ini biasanya terjadi ketika ada "
            + " pesan yang berisi sesuatu selain teks."
        )
        e = format_exc()
        print(e)
