import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from telethon import TelegramClient

# ================== 配置文件 ==================
TG_CONFIG_FILE = "tg_config.json"
BOTS_FILE = "bots.json"
STATE_FILE = "state.json"
PROXY_FILE = "proxy.json"
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

# ================== 状态文件 ==================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_sign_date": None, "fail_count": 0, "last_fail_time": None}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_last_sign_date():
    return load_state().get("last_sign_date")

def update_sign_success():
    now = datetime.now()
    state = load_state()
    state.update(
        {
            "last_sign_date": now.strftime("%Y-%m-%d"),
            "last_sign_time": now.strftime("%H:%M:%S"),
            "last_result": "success",
        }
    )
    save_state(state)

# ================== 菜单 ==================
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

# ================== 代理加载 ==================
def load_proxy():
    if not os.path.exists(PROXY_FILE):
        return None
    with open(PROXY_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if not cfg.get("enabled", False):
        return None
    proxy_type = cfg.get("type", "socks5")
    host = cfg.get("host", "127.0.0.1")
    port = cfg.get("port", 7897)
    username = cfg.get("username")
    password = cfg.get("password")
    return (proxy_type, host, port, username, password)

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
    tasks = []

    async def _checkin_one(bot, info):
        await asyncio.sleep(random.randint(5, 15))  # 随机打散
        try:
            if info["type"] == "command":
                await client.send_message(bot, info["cmd"])
                print(f"[{datetime.now()}] Sent {info['cmd']} -> {bot}")
                return True
        except Exception as e:
            print(f"[{datetime.now()}] Failed {bot}: {e}")
        return False

    for bot, info in bots_cfg.items():
        tasks.append(asyncio.create_task(_checkin_one(bot, info)))

    results = await asyncio.gather(*tasks)
    success = sum(1 for r in results if r)
    failed = len(results) - success

    end_time = datetime.now()
    print(
        f"\n[DONE] 本轮签到完成 | "
        f"成功 {success} / 失败 {failed} | "
        f"耗时 {(end_time - start_time).seconds}s\n"
    )

    return success == len(results)

def calc_next_sign_time(hour, minute):
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # 今天已过 → 明天
    if now >= target:
        target += timedelta(days=1)

    return target

async def scheduled_checkin(client, bots_cfg, hour, minute):
    print(f"[+] 定时签到已启动：{hour:02d}:{minute:02d}")
    print("[INFO] 已启用低流量模式（非轮询）")

    while True:
        state = load_state()
        last_sign = state.get("last_sign_date")
        today = datetime.now().strftime("%Y-%m-%d")

        # 今天还没签，且已经过了目标时间 → 立即补签
        now = datetime.now()
        target_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if last_sign != today and now >= target_today:
            print(f"[INFO] 触发补签（{today}）")
            ok = await send_checkin(client, bots_cfg)
            if ok:
                update_sign_success()
                print("[STATE] 补签成功")
            else:
                print("[WARN] 补签失败，明天自动再试")

        # 计算下一次签到时间
        next_time = calc_next_sign_time(hour, minute)
        sleep_seconds = (next_time - datetime.now()).total_seconds()

        print(f"[INFO] 下次签到时间：{next_time}（sleep {int(sleep_seconds)}s）")

        # 核心：一次性 sleep，到点再醒
        await asyncio.sleep(sleep_seconds)

        print(f"[INFO] 触发定时签到（{next_time.date()}）")
        ok = await send_checkin(client, bots_cfg)
        if ok:
            update_sign_success()
            print("[STATE] 定时签到成功")
        else:
            print("[WARN] 定时签到失败，将在下次周期重试")


# ================== 心跳保持 ==================
async def keep_alive(client):
    while True:
        await client.get_me()
        await asyncio.sleep(300)


# ================== 主入口 ==================
async def main():
    try:
        tg_cfg = load_tg_config()
        bots_cfg = load_bots_config()
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {e}")
        return

    # 根据 proxy.json 判断是否启用代理
    proxy = load_proxy()
    proxy_enabled = bool(proxy)
    if proxy_enabled:
        print(f"[INFO] 代理已启用: {proxy[0]}://{proxy[1]}:{proxy[2]}")
    else:
        print("[INFO] 未启用代理，直接连接 Telegram")

    async with TelegramClient(
        tg_cfg["session_name"],
        tg_cfg["api_id"],
        tg_cfg["api_hash"],
        proxy=proxy,
        connection_retries=999999,
        auto_reconnect=True,
    ) as client:
        asyncio.create_task(keep_alive(client))

        while True:
            show_menu()
            choice = input("请选择功能 (1-5): ").strip()

            if choice == "1":
                await list_all_bots(client, bots_cfg)
            elif choice == "2":
                await send_checkin(client, bots_cfg)
            elif choice == "3":
                hour, minute = get_sign_time()
                await scheduled_checkin(client, bots_cfg, hour, minute)
            elif choice == "4":
                await send_checkin(client, bots_cfg)
                hour, minute = get_sign_time()
                await scheduled_checkin(client, bots_cfg, hour, minute)
            elif choice == "5":
                break
            else:
                print("无效选择，请重试")

    print("Bye.")


if __name__ == "__main__":
    asyncio.run(main())
