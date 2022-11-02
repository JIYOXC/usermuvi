import asyncio
from inspect import getfullargspec

from pyrogram import Client, filters

from MusicAndVideo.config import SUDO_USERS
from MusicAndVideo.helpers.filters import command


async def eor(msg):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


@Client.on_message(filters.user(SUDO_USERS) & command(["del"]))
async def del_user(_, message):
    rep = message.reply_to_message
    await message.delete()
    await rep.delete()


@Client.on_message(command(["linkoceanAntiTinjauDisini"]))
async def wdel_user(_, message):
    await message.delete()


@Client.on_message(filters.user(SUDO_USERS) & command(["purgeme"]))
async def purge_me_func(client, message):
    if len(message.command) != 2:
        return await message.delete()
    n = (
        message.reply_to_message.text
        if message.reply_to_message
        else message.text.split(None, 1)[1].strip()
    )

    if not n.isnumeric():
        return await eor(message, text="Argumen Tidak Valid")

    n = int(n)

    if n < 1:
        return await eor(message, text="Butuh nomor >=1-999")

    chat_id = message.chat.id

    message_ids = [
        m.message_id
        async for m in client.search_messages(
            chat_id,
            from_user=int(message.from_user.id),
            limit=n,
        )
    ]

    if not message_ids:
        return await eor(message, text="Tidak ada pesan yang ditemukan.")

    to_delete = [message_ids[i : i + 999] for i in range(0, len(message_ids), 999)]

    for hundred_messages_or_less in to_delete:
        await client.delete_messages(
            chat_id=chat_id,
            message_ids=hundred_messages_or_less,
            revoke=True,
        )
        mmk = await message.reply(f"✅ {n} Pesan Telah Di Hapus")
        await asyncio.sleep(2)
        await mmk.delete()


@Client.on_message(filters.user(SUDO_USERS) & command(["purge"]))
async def purgefunc(client, message):
    await message.delete()

    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to purge from.")

    chat_id = message.chat.id
    message_ids = []

    for message_id in range(
        message.reply_to_message.message_id,
        message.message_id,
    ):
        message_ids.append(message_id)

        if len(message_ids) == 100:
            await client.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,  # For both sides
            )

            message_ids = []

    if len(message_ids) > 0:
        await client.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True,
        )
