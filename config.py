import json
import os

TG_CONFIG_FILE = "tg_config.json"
BOTS_FILE = "bots.json"
PROXY_FILE = "proxy.json"


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


def load_proxy(path=PROXY_FILE):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if not cfg.get("enabled", False):
        return None
    return (
        cfg.get("type", "socks5"),
        cfg.get("host", "127.0.0.1"),
        cfg.get("port", 7897),
        cfg.get("username") or None,
        cfg.get("password") or None,
    )
