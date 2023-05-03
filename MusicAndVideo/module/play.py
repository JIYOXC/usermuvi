import asyncio
import os
import sys
from random import randint

from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.raw.functions.phone import CreateGroupCall
from pytgcalls import StreamType
from pytgcalls.exceptions import GroupCallNotFound, NoActiveGroupCall
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (HighQualityAudio,
                                                  HighQualityVideo)
from youtubesearchpython import VideosSearch

from MusicAndVideo.config import call_py
from MusicAndVideo.helpers.filters import command
from MusicAndVideo.helpers.other.generator.thumbnail import gen_thumb
from MusicAndVideo.helpers.queues import QUEUE, add_to_queue, get_queue


def YouTube_Search(query):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = f"https://youtu.be/{data['id']}"
        duration = data["duration"]
        id = data["id"]
        return [songname, url, duration, id]
    except Exception as e:
        print(e)
        return 0


async def YouTube_Download(link: str):
    process = await asyncio.create_subprocess_shell(
        f'yt-dlp -g -f "best[height<=?720][width<=?1280]" {link}',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return (1, stdout.decode().strip()) if stdout else (0, stderr.decode().strip())


@Client.on_message(command(["play"]) & filters.group & ~filters.edited)
async def play(client, message):
    if len(message.command) < 2:
        await message.reply(
            f"""
**{message.from_user.mention} Untuk memutar musik silahkan kirim perintah
Contoh: `/play happy asmara lemah teles`**
"""
        )
    else:
        pesan = await message.reply("🔎 Pencarian")
        query = message.text.split(None, 1)[1]
        search = YouTube_Search(query)
        if search == 0:
            await pesan.edit("`Tidak Menemukan Apapun untuk Kueri yang Diberikan`")
        else:
            songname = search[0]
            foto = search[3]
            url = search[1]
            duration = search[2]
            request = message.from_user.mention
            hm, ytlink = await YouTube_Download(url)
            chat_id = message.chat.id
            if hm == 0:
                await pesan.edit(f"**YTDL ERROR ⚠️** \n\n`{ytlink}`")
                await asyncio.sleep(2)
                await pesan.edit("🙏 Mohon maaf kak system nya sedang error")
                await asyncio.sleep(3)
                await pesan.edit(
                    "🔄 System akan segera di restart silahkan tunggu 10 detik lagi"
                )
                os.execl(sys.executable, sys.executable, *sys.argv)
                sys.exit()
            elif chat_id in QUEUE:
                pos = add_to_queue(
                    chat_id,
                    songname,
                    ytlink,
                    foto,
                    "Music",
                    request,
                    duration,
                )
                await pesan.delete()
                thumb = await gen_thumb(foto, "QUEUED TRACK")
                loli = await message.reply_photo(
                    photo=f"{thumb}",
                    caption=f"""
💡 **Music Ditambahkan Ke Antrian > {pos}**

🏷️ **Nama:** [{songname}]({url})
⏱️ **Durasi:** {duration}
🎧 **Atas Permintaan:** {request}
""",
                )
                if os.path.exists(thumb):
                    os.remove(thumb)
                await asyncio.sleep(31)
                await message.delete()
                await loli.delete()
            else:
                while True:
                    try:
                        await call_py.join_group_call(
                            chat_id,
                            AudioPiped(
                                ytlink,
                            ),
                            stream_type=StreamType().pulse_stream,
                        )
                    except (NoActiveGroupCall, GroupCallNotFound):
                        try:
                            await client.send(
                                CreateGroupCall(
                                    peer=await client.resolve_peer(chat_id),
                                    random_id=randint(0, 2147483647),
                                )
                            )
                        except ChatAdminRequired as err:
                            return await pesan.edit(f"`{err}`")
                    else:
                        break
                add_to_queue(
                    chat_id,
                    songname,
                    ytlink,
                    foto,
                    "Music",
                    request,
                    duration,
                )
                await pesan.delete()
                thumb = await gen_thumb(foto, "NOW PLAYING")
                loli = await message.reply_photo(
                    photo=f"{thumb}",
                    caption=f"""
▶️ **Memutar Music**

🏷️ **Nama:** [{songname}]({url})
⏱️ **Durasi:** {duration}
🎧 **Atas Permintaan:** {request}
""",
                )
                if os.path.exists(thumb):
                    os.remove(thumb)
                await asyncio.sleep(31)
                await message.delete()
                await loli.delete()


@Client.on_message(command(["vplay"]) & filters.group & ~filters.edited)
async def vplay(client, message):
    if len(message.command) < 2:
        await message.reply(
            f"""
**{message.from_user.mention} Untuk memutar video silahkan kirim perintah
Contoh: `/vplay happy asmara cukup`**
"""
        )
    else:
        pesan = await message.reply("**🔎 Pencarian")
        query = message.text.split(None, 1)[1]
        search = YouTube_Search(query)
        if search == 0:
            await pesan.edit("**Tidak Menemukan Apa pun untuk Kueri yang Diberikan**")
        else:
            songname = search[0]
            foto = search[3]
            url = search[1]
            duration = search[2]
            request = message.from_user.mention
            hm, ytlink = await YouTube_Download(url)
            chat_id = message.chat.id
            if hm == 0:
                await pesan.edit(f"**YTDL ERROR ⚠️** \n\n`{ytlink}`")
                await asyncio.sleep(2)
                await pesan.edit("🙏 Mohon maaf kak system nya sedang error")
                await asyncio.sleep(3)
                await pesan.edit(
                    "🔄 System akan segera di restart silahkan tunggu 10 detik lagi"
                )
                os.execl(sys.executable, sys.executable, *sys.argv)
                sys.exit()
            elif chat_id in QUEUE:
                pos = add_to_queue(
                    chat_id,
                    songname,
                    ytlink,
                    foto,
                    "Video",
                    request,
                    duration,
                )
                await pesan.delete()
                thumb = await gen_thumb(foto, "QUEUED TRACK")
                loli = await message.reply_photo(
                    photo=f"{thumb}",
                    caption=f"""
💡 **Video Ditambahkan Ke Antrian > {pos}**

🏷️ **Nama:** [{songname}]({url})
⏱️ **Durasi:** {duration}
🎧 **Atas Permintaan:** {request}
""",
                )
                if os.path.exists(thumb):
                    os.remove(thumb)
                await asyncio.sleep(31)
                await message.delete()
                await loli.delete()
            else:
                while True:
                    try:
                        await call_py.join_group_call(
                            chat_id,
                            AudioVideoPiped(
                                ytlink, HighQualityAudio(), HighQualityVideo()
                            ),
                            stream_type=StreamType().pulse_stream,
                        )
                    except (NoActiveGroupCall, GroupCallNotFound):
                        try:
                            await client.send(
                                CreateGroupCall(
                                    peer=await client.resolve_peer(chat_id),
                                    random_id=randint(0, 2147483647),
                                )
                            )
                        except ChatAdminRequired as err:
                            return await pesan.edit(f"`{err}`")
                    else:
                        break
                add_to_queue(
                    chat_id,
                    songname,
                    ytlink,
                    foto,
                    "Video",
                    request,
                    duration,
                )
                await pesan.delete()
                thumb = await gen_thumb(foto, "NOW PLAYING")
                loli = await message.reply_photo(
                    photo=f"{thumb}",
                    caption=f"""
▶️ **Memutar Video**

🏷️ **Nama:** [{songname}]({url})
⏱️ **Durasi:** {duration}
🎧 **Atas Permintaan:** {request}
""",
                )
                if os.path.exists(thumb):
                    os.remove(thumb)
                await asyncio.sleep(31)
                await message.delete()
                await loli.delete()


@Client.on_message(command(["playlist"]) & filters.group & ~filters.edited)
async def playlist(_, message):
    chat_id = message.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            loli = await message.reply(
                f"""
**▶️ Sekarang Memutar: {chat_queue[0][3]}**
**🏷️ Nama:** [{chat_queue[0][0]}](https://youtu.be/{chat_queue[0][2]})**
**🎧 Atas Permintaan: {chat_queue[0][4]}**
""",
                disable_web_page_preview=True,
            )
        else:
            l = len(chat_queue)
            QUE = f"**▶️ Sekarang Memutar: {chat_queue[0][3]}** \n**🏷️ Nama:** [{chat_queue[0][0]}](https://youtu.be/{chat_queue[0][2]})**\n**🎧 Atas Permintaan: {chat_queue[0][4]}**\n\n**⏯ Daftar Antrian:**\n"
            for x in range(1, l):
                hmm = chat_queue[x][0]
                hmmm = chat_queue[x][2]
                hmmmm = chat_queue[x][3]
                request = chat_queue[x][4]
                QUE = f"{QUE}**#{x}: [{hmm}](https://youtu.be/{hmmm}) - ({hmmmm})\n**🎧 Atas Permintaan: {request}**\n\n"
            loli = await message.reply(QUE, disable_web_page_preview=True)
        await asyncio.sleep(15)
        await message.delete()
        await loli.delete()
    else:
        await message.reply("**❌ Tidak memutar apapun**")
