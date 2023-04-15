import os
import re
import textwrap

import aiofiles
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont,
                 ImageOps)
from youtubesearchpython import VideosSearch

YOUTUBE_IMG_URL = os.getenv(
    "https://telegra.ph/file/16137a6bbfa67a7198ad9.jpg",
)


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


async def gen_thumb(foto, status):
    if os.path.isfile(f"search/{foto}.png"):
        return f"search/{foto}.png"

    url = f"https://youtu.be/{foto}"
    try:
        results = VideosSearch(url, limit=1)
        for result in results.result()["result"]:
            try:
                title = result["title"]
                title = re.sub(r"\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session, session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"search/thumb{foto}.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

        youtube = Image.open(f"search/thumb{foto}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)
        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((520, 520), Image.ANTIALIAS)
        logo = ImageOps.expand(logo, border=15, fill="white")
        background.paste(logo, (50, 100))
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype(
            "MusicAndVideo/helpers/other/choose/Roboto-Light.ttf", 40
        )
        font2 = ImageFont.truetype(
            "MusicAndVideo/helpers/other/choose/finalfont.ttf", 35
        )
        font3 = ImageFont.truetype(
            "MusicAndVideo/helpers/other/choose/finalfont.ttf", 75
        )
        para = textwrap.wrap(title, width=32)
        j = 0
        draw.text(
            (600, 150),
            f"{status}",
            fill="white",
            stroke_width=2,
            stroke_fill="white",
            font=font3,
        )
        for line in para:
            if j == 1:
                j += 1
                draw.text(
                    (600, 340),
                    f"{line}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
            if j == 0:
                j += 1
                draw.text(
                    (600, 280),
                    f"{line}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )

        draw.text(
            (600, 450),
            f"Ditonton : {views}",
            (255, 255, 255),
            font=font2,
        )
        draw.text(
            (600, 500),
            f"Durasi : {duration}",
            (255, 255, 255),
            font=font2,
        )
        draw.text(
            (600, 550),
            f"Channel : {channel}",
            (255, 255, 255),
            font=font2,
        )
        try:
            os.remove(f"search/thumb{foto}.png")
        except:
            pass
        background.save(f"search/{foto}.png")
        return f"search/{foto}.png"
    except Exception:
        return YOUTUBE_IMG_URL
