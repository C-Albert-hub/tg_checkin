import asyncio
from telethon import TelegramClient


def build_client(tg_cfg: dict, proxy=None) -> TelegramClient:
    return TelegramClient(
        tg_cfg["session_name"],
        tg_cfg["api_id"],
        tg_cfg["api_hash"],
        proxy=proxy,
        connection_retries=999999,
        auto_reconnect=True,
    )


async def keep_alive(client: TelegramClient):
    while True:
        try:
            if not client.is_connected():
                print("[WARN] keepalive: 连接断开，尝试重连...")
                await client.connect()
            await client.get_me()
        except Exception as e:
            print(f"[WARN] keepalive failed: {e}，5秒后重试...")
            await asyncio.sleep(5)
            continue
        await asyncio.sleep(300)
