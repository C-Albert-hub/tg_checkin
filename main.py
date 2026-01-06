import asyncio
import json
import os
import random
from datetime import datetime
from telethon import TelegramClient

# ================== 配置文件 ==================
TG_CONFIG_FILE = "tg_config.json"
BOTS_FILE = "bots.json"
# =============================================


# ================== 加载配置 ==================
def load_tg_config(path=TG_CONFIG_FILE):
    if not os.path.exists(path):
        raise FileNotFoundError(f"未找到 {path}")

    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    for k in ("api_id", "api_hash", "session_name"):
        if k not in cfg:
            raise ValueError(f"{path} 缺少字段: {k}")

    return cfg


def load_bots_config(path=BOTS_FILE):
    if not os.path.exists(path):
        raise FileNotFoundError(f"未找到 {path}")

    with open(path, "r", encoding="utf-8") as f:
        bots = json.load(f)

    if not isinstance(bots, dict) or not bots:
        raise ValueError("bots.json 内容为空或格式不正确")

    return bots


# ================== 菜单与输入 ==================
def show_menu():
    print("""
================ Telegram Checkin Menu ================
1. 列出所有已添加的机器人
2. 立即签到
3. 定时签到
4. 立即签到 + 定时签到
5. 退出
=======================================================
""")


def get_sign_time():
    while True:
        try:
            hour = int(input("小时 (0-23): ").strip())
            minute = int(input("分钟 (0-59): ").strip())
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                print(f"[OK] 已设置定时签到时间：{hour:02d}:{minute:02d}")
                return hour, minute
            print("[-] 时间范围不合法")
        except ValueError:
            print("[-] 请输入数字")


# ================== 功能实现 ==================
async def list_all_bots(client, bots_cfg):
    print("=== Bots in your account ===")
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if getattr(entity, "bot", False):
            username = entity.username
            flag = "已配置" if username in bots_cfg else "未配置"
            print(f"Name     : {dialog.name}")
            print(f"Username : {username}   [{flag}]")
            print("-" * 40)


async def send_checkin(client, bots_cfg):
    start_time = datetime.now()
    success = 0
    failed = 0

    for bot, info in bots_cfg.items():
        await asyncio.sleep(random.randint(5, 15))
        try:
            if info["type"] == "command":
                await client.send_message(bot, info["cmd"])
                success += 1
                print(f"[{datetime.now()}] Sent {info['cmd']} -> {bot}")
        except Exception as e:
            failed += 1
            print(f"[{datetime.now()}] Failed {bot}: {e}")

    end_time = datetime.now()
    print(
        f"\n[DONE] 本轮签到完成 | "
        f"成功 {success} / 失败 {failed} | "
        f"耗时 {(end_time - start_time).seconds}s\n"
    )


async def scheduled_checkin(client, bots_cfg, hour, minute):
    print(f"[+] 定时签到已启动：{hour:02d}:{minute:02d}")
    try:
        while True:
            now = datetime.now()
            if now.hour == hour and now.minute == minute:
                await send_checkin(client, bots_cfg)
                print(f"[+] 定时签到完成，等待下一次触发...")
                await asyncio.sleep(61)  # 防止重复触发
            await asyncio.sleep(20)
    except asyncio.CancelledError:
        pass


# ================== 短任务统一出口 ==================
async def handle_short_task(func, name):
    await func()
    print(f"[DONE] {name}")
    while True:
        choice = input("\n 输入 b 返回菜单，输入 q 退出: ").strip().lower()
        if choice in ("b", "q"):
            return choice
        print("\n 请输入 b 或 q")


# ================== 心跳保持 ==================
async def keep_alive(client):
    while True:
        try:
            await client.get_me()
        except Exception as e:
            print(f"[WARN] keepalive failed: {e}")
        await asyncio.sleep(300)


# ================== 主入口 ==================
async def main():
    try:
        tg_cfg = load_tg_config()
        bots_cfg = load_bots_config()
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {e}")
        return

    async with TelegramClient(
        tg_cfg["session_name"],
        tg_cfg["api_id"],
        tg_cfg["api_hash"],
        connection_retries=999999,  # 实际无限重连
        auto_reconnect=True
    ) as client:

        # 启动心跳保持
        asyncio.create_task(keep_alive(client))

        while True:
            show_menu()
            choice = input("请选择功能 (1-5): ").strip()

            if choice == "1":
                action = await handle_short_task(
                    lambda: list_all_bots(client, bots_cfg),
                    "列出机器人"
                )
                if action == "q":
                    break

            elif choice == "2":
                action = await handle_short_task(
                    lambda: send_checkin(client, bots_cfg),
                    "立即签到"
                )
                if action == "q":
                    break

            elif choice == "3":
                hour, minute = get_sign_time()
                # 定时签到常驻，不返回菜单
                await scheduled_checkin(client, bots_cfg, hour, minute)
                break

            elif choice == "4":
                await send_checkin(client, bots_cfg)
                hour, minute = get_sign_time()
                # 立即签到+定时签到常驻
                await scheduled_checkin(client, bots_cfg, hour, minute)
                break

            elif choice == "5":
                break

            else:
                print("无效选择，请重试")

    print("Bye.")


if __name__ == "__main__":
    asyncio.run(main())
