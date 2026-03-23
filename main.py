import asyncio
from config import load_tg_config, load_bots_config, load_proxy
from client import build_client, keep_alive
from checkin import run_checkin
from scheduler import scheduled_loop
from menu import show_menu, get_sign_time, list_all_bots


async def main():
    try:
        tg_cfg = load_tg_config()
        bots_cfg = load_bots_config()
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {e}")
        return

    proxy = load_proxy()
    if proxy:
        print(f"[INFO] 代理已启用: {proxy[0]}://{proxy[1]}:{proxy[2]}")
    else:
        print("[INFO] 未启用代理，直接连接 Telegram")

    client = build_client(tg_cfg, proxy)
    async with client:
        asyncio.create_task(keep_alive(client))

        while True:
            show_menu()
            choice = input("请选择功能 (1-5): ").strip()

            if choice == "1":
                await list_all_bots(client, bots_cfg)
            elif choice == "2":
                await run_checkin(client, bots_cfg)
            elif choice == "3":
                hour, minute = get_sign_time()
                await scheduled_loop(client, bots_cfg, hour, minute)
            elif choice == "4":
                await run_checkin(client, bots_cfg)
                hour, minute = get_sign_time()
                await scheduled_loop(client, bots_cfg, hour, minute)
            elif choice == "5":
                break
            else:
                print("无效选择，请重试")

    print("Bye.")


if __name__ == "__main__":
    asyncio.run(main())
