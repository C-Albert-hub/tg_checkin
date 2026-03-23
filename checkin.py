import asyncio
import random
from datetime import datetime
from telethon import TelegramClient


async def checkin_one(client: TelegramClient, bot: str, info: dict) -> bool:
    await asyncio.sleep(random.randint(5, 15))
    for attempt in range(3):
        try:
            if not client.is_connected():
                await client.connect()
            if info["type"] == "command":
                await client.send_message(bot, info["cmd"])
                print(f"[{datetime.now()}] Sent {info['cmd']} -> {bot}")
                return True
        except Exception as e:
            print(f"[{datetime.now()}] Failed {bot}: {e}")
            if attempt < 2:
                await asyncio.sleep(5)
    return False


async def run_checkin(client: TelegramClient, bots_cfg: dict) -> tuple[int, int]:
    start = datetime.now()
    tasks = [asyncio.create_task(checkin_one(client, bot, info)) for bot, info in bots_cfg.items()]
    results = await asyncio.gather(*tasks)
    success = sum(1 for r in results if r)
    failed = len(results) - success
    elapsed = (datetime.now() - start).seconds
    print(f"\n[DONE] 本轮签到完成 | 成功 {success} / 失败 {failed} | 耗时 {elapsed}s\n")
    return success, failed
