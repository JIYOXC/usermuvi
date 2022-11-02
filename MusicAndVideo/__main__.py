import asyncio

from pytgcalls import idle

from MusicAndVideo import config


async def main():
    await config.ubot.start()
    await config.call_py.start()
    await idle()


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
