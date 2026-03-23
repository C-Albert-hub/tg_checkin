import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from checkin import run_checkin


async def wait_until(hour: int, minute: int):
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    wait_seconds = (target - now).total_seconds()
    print(f"[INFO] 下次签到时间：{target.strftime('%Y-%m-%d %H:%M:%S')}（sleep {int(wait_seconds)}s）")
    await asyncio.sleep(wait_seconds)


async def scheduled_loop(client: TelegramClient, bots_cfg: dict, hour: int, minute: int):
    print(f"[+] 定时签到已启动：{hour:02d}:{minute:02d}")
    try:
        while True:
            await wait_until(hour, minute)
            print(f"[INFO] 触发定时签到（{datetime.now().strftime('%Y-%m-%d')}）")
            _, failed = await run_checkin(client, bots_cfg)
            if failed:
                print("[WARN] 本次签到失败，将在下一次自动重试")
    except asyncio.CancelledError:
        pass
