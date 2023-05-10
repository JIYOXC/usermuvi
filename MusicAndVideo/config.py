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
    "BQCUpYHt_Ijl5yYnWQg_0u9j9_v4RNVbRF2SiAkskiel28okTE9s6TKsQ5giZdspJf98bhO9Mq93G6XmRcvpmPzO5rjITthxPNCUcxc-J29PinzFiK7xqkRuq6GUS9MLWzfb_UAX1ssAlF1bFfrP4xdpxANSl-V5FR7vvJT59ehBRUFumVpdH81aJKaou5RD_fGLqQ9npOx_opllKBS8xeug2OlHuYX0Wcpt7lOsFQcYshaIkBsfLQECApqAeVTKsR5JU8U0NUykFs5T6aE2rQKpIRbw0j88CPM_nsmPXSkVytaUZcpTlT3FBpk8A5u9HbK0-yiY4GfTxn1LgYvOyJFQAAAAAVd3OfsA",
)
COMMAND_PREFIXES = list(
    os.getenv("COMMAND_PREFIXES", "( . , : ; _ - + ! ? / P )").split()
)
SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", "1654657140").split()))
OWNER_ID = list(map(int, os.getenv("OWNER_ID", "1654657140").split()))
bot = Client(SESSION, API_ID, API_HASH, plugins=dict(root="MusicAndVideo.module"))
call_py = PyTgCalls(bot)
