from telethon import TelegramClient


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


def get_sign_time() -> tuple[int, int]:
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


async def list_all_bots(client: TelegramClient, bots_cfg: dict):
    print("=== Bots in your account ===")
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if getattr(entity, "bot", False):
            username = entity.username
            flag = "已配置" if username in bots_cfg else "未配置"
            print(f"Name     : {dialog.name}")
            print(f"Username : {username}   [{flag}]")
            print("-" * 40)
