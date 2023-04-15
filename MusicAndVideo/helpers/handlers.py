import asyncio
import os

from pytgcalls.types import StreamAudioEnded
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, HighQualityVideo

from MusicAndVideo.config import bot as app
from MusicAndVideo.config import call_py
from MusicAndVideo.helpers.other.generator.thumbnail import gen_thumb
from MusicAndVideo.helpers.queues import QUEUE, clear_queue, get_queue, pop_an_item


async def skip_current_song(chat_id):
    if chat_id not in QUEUE:
        return 0
    chat_queue = get_queue(chat_id)
    if len(chat_queue) == 1:
        await call_py.leave_group_call(chat_id)
        clear_queue(chat_id)
        return 1
    else:
        try:
            songname = chat_queue[1][0]
            url = chat_queue[1][1]
            link = chat_queue[1][2]
            type = chat_queue[1][3]
            request = chat_queue[1][4]
            duration = chat_queue[1][5]
            if type == "Music":
                await call_py.change_stream(
                    chat_id,
                    AudioPiped(
                        url,
                    ),
                )
            elif type == "Video":
                await call_py.change_stream(
                    chat_id,
                    AudioVideoPiped(
                        url,
                        HighQualityAudio(),
                        HighQualityVideo(),
                    ),
                )
            pop_an_item(chat_id)
            return [songname, link, type, request, duration]
        except:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            return 2


async def skip_item(chat_id, h):
    if chat_id not in QUEUE:
        return 0
    chat_queue = get_queue(chat_id)
    try:
        x = int(h)
        songname = chat_queue[x][0]
        chat_queue.pop(x)
        return songname
    except Exception as e:
        print(e)
        return 0


@call_py.on_stream_end()
async def stream_end_handler(_, u):
    if isinstance(u, StreamAudioEnded):
        chat_id = u.chat_id
        op = await skip_current_song(chat_id)
        if op == 1:
            loli = await app.send_message(
                chat_id,
                """
**✅ Antrian kosong.

• Meninggalkan obrolan suara**
""",
            )
        elif op == 2:
            loli = await app.send_message(
                chat_id,
                """
**❌ terjadi kesalahan

🗑️ Membersihkan antrian dan keluar dari obrolan video.**
""",
            )
        else:
            thumb = await gen_thumb(op[1], "NOW PLAYING")
            loli = await app.send_photo(
                chat_id,
                photo=thumb,
                caption=f"""

**▶️ Sekarang Memutar {op[2]}

🏷️ Nama: [{op[0]}](https://youtu.be/{op[1]})
⏱️ Durasi: {op[4]}
🎧 Atas Permintaan: {op[3]}**
""",
            )
            if os.path.exists(thumb):
                os.remove(thumb)

        await asyncio.sleep(31)
        await loli.delete()


@call_py.on_closed_voice_chat()
@call_py.on_kicked()
@call_py.on_left()
async def __(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
