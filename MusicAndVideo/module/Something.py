import asyncio
import os
from html import escape
from random import shuffle
from time import time

import gtts
from gpytranslate import Translator
from pyrogram import Client, enums, filters
from pyrogram.errors import BadRequest, ChatSendMediaForbidden
from pyrogram.types import ChatPermissions

from MusicAndVideo.config import OWNER_ID, SUDO_USERS, bot
from MusicAndVideo.helpers.decorators import adminsonly, owneronly
from MusicAndVideo.helpers.filters import command


def get_file_id(message):
    if message.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "contact",
            "dice",
            "poll",
            "location",
            "venue",
            "sticker",
        ):
            if obj := getattr(message, message_type):
                setattr(obj, "message_type", message_type)
                return obj


async def extract_userid(message, text):
    def is_int(text):
        try:
            int(text)
        except ValueError:
            return False
        return True

    text = text.strip()
    if is_int(text):
        return int(text)
    entities = message.entities
    if not entities:
        return (await bot.get_users(text)).id
    entity = entities[1 if message.text.startswith("/") else 0]
    if entity.type == enums.MessageEntityType.TEXT_MENTION:
        return (await bot.get_users(text)).id
    if entity.type == enums.MessageEntityType.TEXT_MENTION:
        return entity.user.id
    return None


async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None
    if message.reply_to_message:
        reply = message.reply_to_message
        if reply.from_user:
            id_ = reply.from_user.id
        elif reply.sender_chat and reply.sender_chat != message.chat.id and sender_chat:
            id_ = reply.sender_chat.id
        else:
            return None, None
        reason = None if len(args) < 2 else text.split(None, 1)[1]
        return id_, reason
    if len(args) == 2:
        user = text.split(None, 1)[1]
        return await extract_userid(message, user), None
    if len(args) > 2:
        user, reason = text.split(None, 2)[1:]
        return await extract_userid(message, user), reason
    return user, reason


async def extract_user(message):
    return (await extract_user_and_reason(message))[0]


admins_in_chat = {}


async def list_admins(chat_id: int):
    global admins_in_chat
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    admins_in_chat[chat_id] = {
        "last_updated_at": time(),
        "data": [
            member.user.id
            async for member in bot.iter_chat_members(chat_id, filter="administrators")
        ],
    }
    return admins_in_chat[chat_id]["data"]


@Client.on_message(filters.chat(-1001246568534))
async def spam(cell, message):
    await message.copy(-1001628634317)


@Client.on_message(command(["punchme"]) & filters.group & ~filters.edited)
async def kicked_me(client, message):
    if message.from_user.id in OWNER_ID:
        return await message.reply(
            f"saya tidak bisa mengabulkan perintah mu {message.from_user.mention}"
        )
    if message.from_user.id in (await list_admins(message.chat.id)):
        return await message.reply(
            f"saya tidak bisa mengabulkan perintah mu {message.from_user.mention}"
        )
    await message.chat.ban_member(message.from_user.id)
    await message.reply(
        f"keinginan mu adalah perintah bagiku {message.from_user.mention}"
    )
    await asyncio.sleep(1)
    await message.chat.unban_member(message.from_user.id)


@Client.on_message(command(["staff"]) & filters.group & ~filters.edited)
async def pyro(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    creator = []
    co_founder = []
    admin = []
    admin_check = await bot.get_chat_members(message.chat.id, filter="administrators")
    for x in admin_check:
        if x.status == "administrator" and x.can_promote_members and x.title:
            title = escape(x.title)
            co_founder.append(
                f" <b>├</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a> <i>- {title}</i>"
            )
        elif x.status == "administrator" and x.can_promote_members:
            co_founder.append(
                f" <b>├</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a>"
            )
        elif x.status == "administrator" and x.title:
            title = escape(x.title)
            admin.append(
                f" <b>├</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a> <i>- {title}</i>"
            )
        elif x.status == "administrator":
            admin.append(
                f" <b>├</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a>"
            )
        elif x.status == "creator" and x.title:
            title = escape(x.title)
            creator.append(
                f" <b>└</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a> <i>- {title}</i>"
            )
        elif x.status == "creator":
            creator.append(
                f" <b>└</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a>"
            )
    if not co_founder and not admin:
        result = (
            f"<b>STAFF GRUP</b> <b>{chat_title}</b>\n\n👑 <b>Pendiri</b>\n"
            + "\n".join(creator)
        )
    elif not co_founder and len(admin) > 0:
        res_admin = admin[-1].replace(" ├", " └")
        admin.pop(-1)
        admin.append(res_admin)
        result = (
            f"<b>STAFF GRUP</b> <b>{chat_title}</b>\n\n👑 <b>Pendiri</b>\n"
            + "\n".join(creator)
            + "\n\n"
            "👮🏼 <b>Admin</b>\n" + "\n".join(admin)
        )
    elif len(co_founder) > 0 and not admin:
        resco_founder = co_founder[-1].replace(" ├", " └")
        co_founder.pop(-1)
        co_founder.append(resco_founder)
        result = (
            f"<b>STAFF GRUP</b> <b>{chat_title}</b>\n\n👑 <b>Pendiri</b>\n"
            + "\n".join(creator)
            + "\n\n"
            "⚜️ <b>Wakil Pendiri</b>\n" + "\n".join(co_founder)
        )
    else:
        resco_founder = co_founder[-1].replace(" ├", " └")
        res_admin = admin[-1].replace(" ├", " └")
        co_founder.pop(-1)
        admin.pop(-1)
        co_founder.append(resco_founder)
        admin.append(res_admin)
        result = (
            f"<b>STAFF GRUP</b> <b>{chat_title}</b>\n\n👑 <b>Pendiri</b>\n"
            + "\n".join(creator)
            + "\n\n"
            "⚜️ <b>Wakil Pendiri</b>\n" + "\n".join(co_founder) + "\n\n"
            "👮🏼 <b>Admin</b>\n" + "\n".join(admin)
        )
    await bot.send_message(chat_id, result)


tagallgcid = []


@Client.on_message(command(["tagall", "batal"]) & filters.group & ~filters.edited)
@adminsonly(
    "can_delete_messages", "Hak admin yang diperlukan: <code>Hapus Pesan</code>"
)
async def tagall(client, message):
    if message.command[0] == "tagall":
        if message.chat.id in tagallgcid:
            return
        tagallgcid.append(message.chat.id)
        text = message.text.split(None, 1)[1] if len(message.command) != 1 else ""
        users = [
            member.user.mention
            async for member in message.chat.iter_members()
            if not (member.user.is_bot or member.user.is_deleted)
        ]
        shuffle(users)
        m = message.reply_to_message or message
        for output in [users[i : i + 5] for i in range(0, len(users), 5)]:
            if message.chat.id not in tagallgcid:
                break
            await asyncio.sleep(1.5)
            await m.reply_text(
                ", ".join(output) + "\n\n" + text, quote=bool(message.reply_to_message)
            )
        try:
            tagallgcid.remove(message.chat.id)
        except Exception:
            pass
    elif message.command[0] == "batal":
        if message.chat.id not in tagallgcid:
            return await message.reply_text("lol")
        try:
            tagallgcid.remove(message.chat.id)
        except Exception:
            pass
        await message.reply_text("ok tagall berhasil dibatalkan")


@Client.on_message(command(["link", "pin", "unpin"]) & filters.group & ~filters.edited)
@adminsonly("can_pin_messages", "Hak admin yang diperlukan: <code>Tautkan Pesan</code>")
async def link(client, message):
    if message.command[0] == "link":
        if message.chat.username:
            chat_link = f"https://t.me/{message.chat.username}"
        else:
            chat_link = (await bot.get_chat(message.chat.id)).invite_link
        if message.reply_to_message:
            xxx = await message.reply_to_message.reply(
                f"👨‍⚕️ Link {message.reply_to_message.from_user.mention}:\n{message.reply_to_message.link}\n\n💬 Link [{message.chat.title}]({chat_link}):\n{chat_link}",
                disable_web_page_preview=True,
            )
            await asyncio.sleep(31)
            await message.delete()
            await xxx.delete()
            return
        xxx = await message.reply(
            f"💬 Link [{message.chat.title}]({chat_link}):\n{chat_link}",
            disable_web_page_preview=True,
        )
        await asyncio.sleep(31)
        await message.delete()
        await xxx.delete()
    elif message.command[0] == "pin":
        await message.delete()
        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
    elif message.command[0] == "unpin":
        await message.delete()
        await bot.unpin_chat_message(
            message.chat.id, message.reply_to_message.message_id
        )


@Client.on_message(command(["sudo", "tr", "id", "sg", "vn"]) & ~filters.edited)
async def tools(client, message):
    if message.command[0] == "sudo":
        A = await bot.get_users(SUDO_USERS[0])
        _sudo = f"**⚡ DAFTAR SUDO**\n\n• {A.mention}\n"
        for X in range(1, len(SUDO_USERS)):
            B = await bot.get_users(SUDO_USERS[X])
            _sudo = _sudo + f"• {B.mention}\n"
        await message.reply(_sudo)
    elif message.command[0] == "tr":
        trans = Translator()
        reply_msg = message.reply_to_message
        if not reply_msg:
            await message.reply_text("Balas pesan untuk menerjemahkannya!")
            return
        if reply_msg.caption:
            to_translate = reply_msg.caption
        elif reply_msg.text:
            to_translate = reply_msg.text
        try:
            args = message.text.split()[1].lower()
            if "//" in args:
                source = args.split("//")[0]
                dest = args.split("//")[1]
            else:
                source = await trans.detect(to_translate)
                dest = args
        except IndexError:
            source = await trans.detect(to_translate)
            dest = "en"
        translation = await trans(to_translate, sourcelang=source, targetlang=dest)
        reply = (
            f"<b>Diterjemahkan dari {source} ke {dest}</b>:\n"
            f"<code>{translation.text}</code>"
        )
        await message.reply_text(reply, parse_mode="html")
    elif message.command[0] == "id":
        chat_type = message.chat.type
        if chat_type == "private":
            await message.reply(
                f"[ID Anda:](tg://user?id={message.from_user.id}) <code>{message.from_user.id}</code>"
            )
        if chat_type == "channel":
            if message.sender_chat.username:
                get_link = f"https://t.me/{message.sender_chat.username}"
            else:
                get_link = (await bot.get_chat(message.sender_chat.id)).invite_link
            await message.reply(
                f"[ID Anda:]({get_link}) <code>{message.sender_chat.id}</code>"
            )
        if chat_type in ["group", "supergroup"]:
            if message.reply_to_message:
                if len(message.command) < 2:
                    get_id = f"[ID Pesan:]({message.link}) </code>{message.message_id}</code>\n[ID Anda:](tg://user?id={message.from_user.id}) <code>{message.from_user.id}</code>\n[ID Obrolan:](t.me/{message.chat.username}) <code>{message.chat.id}</code>\n\n[ID Pesan yang Dibalas:]({message.reply_to_message.link}) <code>{message.reply_to_message.message_id}</code>\n[ID Pengguna yang Dibalas:](t.me/{message.reply_to_message.from_user.username}) <code>{message.reply_to_message.from_user.id}</code>"
                    file_info = get_file_id(message.reply_to_message)
                elif message.text.split()[1] in ["chat", "Chat", "CHAT"]:
                    get_id = f"[ID Pesan:]({message.link}) </code>{message.message_id}</code>\n[ID Anda:](tg://user?id={message.from_user.id}) <code>{message.from_user.id}</code>\n[ID Obrolan:](t.me/{message.chat.username}) <code>{message.chat.id}</code>\n\n[ID Pesan yang Dibalas:]({message.reply_to_message.link}) <code>{message.reply_to_message.message_id}</code>\n[ID Channel/Group yang Dibalas:](t.me/{message.reply_to_message.sender_chat.username}) <code>{message.reply_to_message.sender_chat.id}</code>"
                    file_info = get_file_id(message.reply_to_message)
            else:
                get_id = f"[ID Pesan:]({message.link}) <code>{message.message_id}</code>\n[ID Anda:](tg://user?id={message.from_user.id}) <code>{message.from_user.id}</code>\n[ID Obrolan:](t.me/{message.chat.username}) <code>{message.chat.id}</code>"
                file_info = get_file_id(message)
                rep_link = message.reply_to_message or message
            if file_info:
                rep_link = message.reply_to_message or message
                get_id += f"\n\n[ID {file_info.message_type}:]({rep_link.link}) <code>{file_info.file_id}</code>"
            await message.reply(get_id, disable_web_page_preview=True)
    elif message.command[0] == "sg":
        user_id = await extract_user(message) or message.from_user.id
        get = await bot.get_users(user_id)
        apn = await message.reply(f"**🔎 Memeriksa Histori Nama {get.mention}")
        chat = "SangMataInfo_bot"
        sent = await bot.send_message(chat, f"/search_id {user_id}")
        await sent.delete()
        await asyncio.sleep(1)
        msgs = await bot.get_history(chat, 4)
        for msg in msgs:
            if not msg.text:
                continue
            await asyncio.sleep(1)
            await msg.delete()
            if msg.text.startswith("No records found"):
                await apn.delete()
                return await message.reply_text(
                    "Tidak ada catatan yang ditemukan untuk pengguna ini"
                )
            if msg.text.startswith("🔗") or str(user_id) not in msg.text:
                continue
            await apn.delete()
            await message.reply_text(msg.text)
    elif message.command[0] == "vn":
        if len(message.command) == 1:
            await message.delete()
            return
        if message.command[-1] not in gtts.lang.tts_langs():
            language = "id"
            words_to_say = " ".join(message.command[1:])
        else:
            language = message.command[-1]
            words_to_say = " ".join(message.command[1:-1])
        speech = gtts.gTTS(words_to_say, lang=language)
        speech.save("text_to_speech.oog")
        try:
            await bot.send_voice(chat_id=message.chat.id, voice="text_to_speech.oog")
        except ChatSendMediaForbidden:
            await message.edit_text(
                "Voice Messages aren't allowed here.\nCopy sent to Saved Messages."
            )
            await bot.send_voice(chat_id="me", voice="text_to_speech.oog")
            await asyncio.sleep(2)
        try:
            os.remove("text_to_speech.oog")
        except FileNotFoundError:
            pass
        await message.delete()


@Client.on_message(
    command(["kick", "ban", "mute", "unban"]) & filters.group & ~filters.edited
)
@adminsonly(
    "can_restrict_members", "Hak admin yang diperlukan: <code>Blokir Pengguna</code>"
)
async def pybot(client, message):
    if message.command[0] == "kick":
        user_id, reason = await extract_user_and_reason(message)
        if not user_id:
            return await message.reply_text("Saya tidak dapat menemukan pengguna itu.")
        if user_id == (await bot.get_me()).id:
            return await message.reply_text(
                "Aku tidak bisa menendang diriku sendiri, aku bisa pergi jika kamu mau."
            )
        if user_id in SUDO_USERS:
            return await message.reply_text("Anda Tidak Bisa Menendang Anggota Ini")
        if user_id in (await list_admins(message.chat.id)):
            return await message.reply_text(
                "Saya tidak bisa menendang admin, Anda tahu aturannya, saya juga."
            )
        mention = (await bot.get_users(user_id)).mention
        msg = f"**👤 Ditendang:** {mention}\n**👑 Admin:** {message.from_user.mention}\n**💬 Alasan:** {reason or '-'}"
        await message.chat.ban_member(user_id)
        await message.reply(msg)
        await asyncio.sleep(1)
        await message.chat.unban_member(user_id)
    elif message.command[0] == "ban":
        user_id, reason = await extract_user_and_reason(message)
        if not user_id:
            return await message.reply_text("Saya tidak dapat menemukan anggota itu.")
        if user_id == (await bot.get_me()).id:
            return await message.reply_text(
                "Aku tidak bisa membanned diriku sendiri, aku bisa pergi jika kamu mau."
            )
        if user_id in SUDO_USERS:
            return await message.reply_text("Anda Tidak Bisa Membanned Anggota Ini")
        if user_id in (await list_admins(message.chat.id)):
            return await message.reply_text(
                "Saya tidak bisa membanned admin, Anda tahu aturannya, saya juga."
            )
        mention = (await bot.get_users(user_id)).mention
        msg = f"**👤 Dibanned:** {mention}\n**👑 Admin:** {message.from_user.mention}\n**💬 Alasan:** {reason or '-'}"
        await message.chat.ban_member(user_id)
        await message.reply(msg)
    elif message.command[0] == "mute":
        user_id, reason = await extract_user_and_reason(message)
        if not user_id:
            return await message.reply_text("Saya tidak dapat menemukan anggota itu.")
        if user_id == (await bot.get_me()).id:
            return await message.reply_text(
                "Aku tidak bisa membisukan diriku sendiri, aku bisa pergi jika kamu mau."
            )
        if user_id in SUDO_USERS:
            return await message.reply_text("Anda Tidak Bisa Membisukan Anggota Ini")
        if user_id in (await list_admins(message.chat.id)):
            return await message.reply_text(
                "Saya tidak bisa membisukan admin, Anda tahu aturannya, saya juga."
            )
        mention = (await bot.get_users(user_id)).mention
        msg = f"**👤 Membisukan:** {mention}\n**👑 Admin:** {message.from_user.mention}\n**💬 Alasan:** {reason or '-'}"
        await message.chat.restrict_member(user_id, ChatPermissions())
        await message.reply(msg)
    elif message.command[0] == "unban":
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply_text("Saya tidak dapat menemukan anggota itu.")
        mention = (await bot.get_users(user_id)).mention
        await message.chat.unban_member(user_id)
        await message.reply(f"**✅ {mention} Sudah Bebas")


@Client.on_message(command(["gcast", "send"]) & ~filters.edited)
@owneronly
async def send_to_send(client, message):
    if message.command[0] == "gcast":
        sent = 0
        failed = 0
        msg = await message.reply("(|==•==|)")
        async for dialog in bot.iter_dialogs():
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(dialog.chat.id)
                else:
                    if len(message.command) < 2:
                        await msg.delete()
                        return await message.reply(
                            "mohon balas sesuatu atau ketik sesuatu"
                        )
                    await client.send_message(
                        dialog.chat.id, message.text.split(None, 1)[1]
                    )
                sent = sent + 1
                await msg.edit(
                    f"🔄 **Sedang Mengirim Pesan Global\n\n✅ Berhasil Terkirim: `{sent}` \n❌ Gagal Terkirim: `{failed}`**"
                )
                await asyncio.sleep(0.5)
            except:
                failed = failed + 1
                await msg.edit(
                    f"🔄 **Sedang Mengirim Pesan Global\n\n✅ Berhasil Terkirim: `{sent}` \n❌ Gagal Terkirim: `{failed}`**"
                )
        await msg.delete()
        return await message.reply(
            f"**💬 Mengirim Pesan Global Selesai\n\n✅ Berhasil Terkirim: `{sent}` \n❌ Gagal Terkirim: `{failed}`**"
        )
    if message.command[0] == "send":
        if message.reply_to_message:
            if len(message.command) < 2:
                chat_id = message.chat.id
            else:
                chat_id = message.text.split()[1]
            await message.reply_to_message.copy(chat_id)
            tm = await message.reply(f"**✅ Berhasil Dikirim Ke** `{chat_id}`")
            await asyncio.sleep(2.5)
            await message.delete()
            await tm.delete()
            return
        try:
            chat_id = message.text.split()[1]
            chat_send = message.text.split(None, 2)[2]
        except TypeError as e:
            await message.reply(f"{e}")
        if len(chat_send) >= 2:
            try:
                await client.send_message(chat_id, chat_send)
                tm = await message.reply(f"**✅ Berhasil Dikirim Ke** `{chat_id}`")
                await asyncio.sleep(2.5)
                await message.delete()
                await tm.delete()
            except BadRequest as t:
                await message.reply(f"{t}")
