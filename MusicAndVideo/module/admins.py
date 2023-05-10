import os

from pyrogram import filters

from MusicAndVideo.config import bot, call_py
from MusicAndVideo.helpers.decorators import adminsonly
from MusicAndVideo.helpers.filters import command
from MusicAndVideo.helpers.handlers import skip_current_song, skip_item
from MusicAndVideo.helpers.other.generator.thumbnail import gen_thumb
from MusicAndVideo.helpers.queues import QUEUE, clear_queue


@bot.on_message(
    filters.group & ~filters.edited & command(["skip", "pause", "resume", "end"])
)
@adminsonly(
    "can_manage_voice_chats",
    "Hak admin yang diperlukan: <code>Manage Live Streams</code>",
)
async def music_ended(_, message):
    if message.command[0] == "skip":
        chat_id = message.chat.id
        if len(message.command) < 2:
            op = await skip_current_song(chat_id)
            if op == 0:
                await message.reply(
                    "**❌ Tidak ada apapun didalam antrian untuk dilewati!**"
                )
            elif op == 1:
                await message.reply("Antrian Kosong, Meninggalkan Obrolan Suara**")
            else:
                thumb = await gen_thumb(op[1], "NOW PLAYING")
                await message.reply_photo(
                    photo=thumb,
                    caption=f"""
**⏭ {message.from_user.mention} Telah Manggganti {op[2]}
🏷️ Nama: [{op[0]}](https://youtu.be/{op[1]})
⏱️ Durasi: {op[4]}
🎧 Atas Permintaan: {op[3]}**
""",
                )
                if os.path.exists(thumb):
                    os.remove(thumb)
                await message.delete()
        else:
            OP = "**🗑️ Menghapus **"
            if chat_id in QUEUE:
                skip = message.text.split(None, 1)[1]
                items = [int(x) for x in skip.split(" ") if x.isdigit()]
                items.sort(reverse=True)
                for x in items:
                    if x != 0:
                        hm = await skip_item(chat_id, x)
                        if hm != 0:
                            OP = OP + "\n" + f"**#{x}** - {hm[:25]} Dari Daftar Antrian"
                await message.reply(OP)
                await message.delete()
    elif message.command[0] == "pause":
        chat_id = message.chat.id
        if chat_id in QUEUE:
            try:
                await call_py.pause_stream(chat_id)
                await message.reply(
                    f"**⏸ Pemutaran dijeda.**\n\n• Untuk melanjutkan pemutaran, gunakan perintah » /resume"
                )
                await message.delete()
            except Exception as e:
                await message.reply(f"**ERROR** \n`{e}`")
        else:
            await message.reply("** ❌ Tidak ada apapun yang sedang diputar!**")
    elif message.command[0] == "resume":
        chat_id = message.chat.id
        if chat_id in QUEUE:
            try:
                await call_py.resume_stream(chat_id)
                await message.reply(
                    f"**▶ Melanjutkan pemutaran yang dijeda**\n\n• Untuk menjeda pemutaran, gunakan perintah » /pause**"
                )
                await message.delete()
            except Exception as e:
                await message.reply(f"**ERROR** \n`{e}`")
        else:
            await message.reply("**❌ Tidak ada apapun yang sedang dijeda!**")
    elif message.command[0] == "end":
        chat_id = message.chat.id
        if chat_id in QUEUE:
            try:
                await call_py.leave_group_call(chat_id)
                clear_queue(chat_id)
                await message.reply(
                    f"**✅ Pemutaran dihentikan oleh: {message.from_user.mention}**"
                )
                await message.delete()
            except Exception as e:
                await message.reply(f"**ERROR** \n`{e}`")
        else:
            await message.reply("**❌ Tidak ada apapun yang sedang diputar!**")
