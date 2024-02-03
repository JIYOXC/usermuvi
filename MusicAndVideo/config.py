import os

from dotenv import load_dotenv
from pyrogram import Client
from pytgcalls import PyTgCalls

# For Local Deploy
if os.path.exists(".env"):
    load_dotenv(".env")
# Necessary Vars
API_ID = int(os.getenv("API_ID", "23781062"))
API_HASH = os.getenv("API_HASH", "fc7ec0cb472d8f100683162e7a10eba8")
SESSION = os.getenv(
    "SESSION",
    "-)
COMMAND_PREFIXES = list(
    os.getenv("COMMAND_PREFIXES", "( . , : ; _ - + ! ? / P )").split()
)
SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", "6724178814").split()))
OWNER_ID = list(map(int, os.getenv("OWNER_ID", "1978415696").split()))
bot = Client(SESSION, API_ID, API_HASH, plugins=dict(root="MusicAndVideo.module"))
call_py = PyTgCalls(bot)
