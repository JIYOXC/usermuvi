from functools import wraps
from traceback import format_exc as err

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from MusicAndVideo.config import OWNER_ID, SUDO_USERS, bot


async def member_permissions(chat_id, user_id):
    perms = []
    member = await ubot.get_chat_member(chat_id, user_id)
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_voice_chats:
        perms.append("can_manage_voice_chats")
    return perms


async def authorised(func, subFunc2, client, message):
    chatID = message.chat.id
    try:
        await func(client, message)
    except ChatWriteForbidden as z:
        await hot.send_message(chatID, z)
    except Exception as e:
        try:
            await message.reply_text(str(e.MESSAGE))
        except AttributeError:
            await message.reply_text(str(e))
        e = err()
        print(str(e))
    return subFunc2


async def unauthorised(message, text_permissions, subFunc2):
    chatID = message.chat.id
    text = "<b>🙏🏻 Maaf {} anda bukan admin group {}\n\n✅ Untuk menggunakan perintah <code>{}</code> harus menjadi admin terlebih dahulu\n\n🔐 {}</b>"
    try:
        await message.reply_text(
            text.format(
                message.from_user.mention,
                message.chat.title,
                message.text.split()[0],
                text_permissions,
            )
        )
    except ChatWriteForbidden as e:
        await bot.send_message(chatID, e)
    return subFunc2


def adminsonly(permission, text_permissions):
    def subFunc(func):
        @wraps(func)
        async def subFunc2(client, message):
            chatID = message.chat.id
            if not message.from_user:
                if message.sender_chat and message.sender_chat.id == message.chat.id:
                    return await authorised(
                        func,
                        subFunc2,
                        client,
                        message,
                    )
                return await unauthorised(message, text_permissions, subFunc2)
            userID = message.from_user.id
            permissions = await member_permissions(chatID, userID)
            if userID not in SUDO_USERS and permission not in permissions:
                return await unauthorised(message, text_permissions, subFunc2)
            return await authorised(func, subFunc2, client, message)

        return subFunc2

    return subFunc


def owneronly(mystic):
    async def wrapper(client, message):
        if message.from_user.id not in OWNER_ID:
            text = "<b>❌ {} Tidak Bisa Menggunakan Perintah {}\n\n✅ {} Yang Bisa Menggunakan Perintah {}</b>"
            user = message.from_user
            command = message.text.split()[0]
            owner = await bot.get_users(OWNER_ID[0])
            return await message.reply_text(
                text.format(
                    user.mention,
                    command,
                    owner.mention,
                    command,
                ),
            )
        return await mystic(client, message)

    return wrapper
