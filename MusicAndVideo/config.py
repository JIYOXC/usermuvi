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
    "BQAAB_gAWVznjzESSgLvP_FQ8F2yCYsKsiu63x5ZrzmbIcAqaojGdGyAiSyDQMeQHbg3r8eHJ9zQs8CSQUtNQs-_Qqlgumd8GV9YjYtEPqXXCb1PDcE1oF3GNHJMh1BJzEF1CGwNCHDM4wDqxYhWGnvK5afPHzAIvfheFqIKYW4GcvOWhXmesDDNFI9AC1VXMx_3TwPZUO9pPXaxyvAXm1SUDGK6nCf8VwdPU9GGG3m97_qblGpqH5DRBnUtmY4l74G0sC_dsR5HXdixE7sgWyGQUVr72NwGtUrepp49TyITsW6DipCPVHretTtqKzTSJScMawhDc28Lf8l9M26mfm2DxqIjxgAAAAB17DpQAA",
)
COMMAND_PREFIXES = list(
    os.getenv("COMMAND_PREFIXES", "( . , : ; _ - + ! ? / P )").split()
)
SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", "1654657140").split()))
OWNER_ID = list(map(int, os.getenv("OWNER_ID", "1654657140").split()))
bot = Client(SESSION, API_ID, API_HASH, plugins=dict(root="MusicAndVideo.module"))
call_py = PyTgCalls(bot)
