# tg_checkin

一个用于 Telegram 机器人自动签到的程序

# 项目结构

```
tg_checkin/
├── main.py              # 入口，启动程序
├── config.py            # 配置加载
├── client.py            # Telegram 客户端管理 & keepalive
├── checkin.py           # 签到核心逻辑
├── scheduler.py         # 定时调度
├── menu.py              # CLI 交互菜单
├── bots.json            # 配置需要签到的机器人
├── tg_config.json       # 配置 api_id 和 api_hash
├── proxy.json           # 代理设置，enabled = false 默认关闭
└── checkin.session      # Telethon 生成的 session 文件
```

# 配置说明

**tg_config.json**
```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "session_name": "checkin"
}
```

**bots.json**
```json
{
  "BotUsername": {
    "type": "command",
    "cmd": "/checkin",
    "desc": "描述"
  }
}
```

**proxy.json**
```json
{
  "enabled": false,
  "type": "socks5",
  "host": "127.0.0.1",
  "port": 7897,
  "username": "",
  "password": ""
}
```

# 效果展示

<img width="858" height="534" alt="image" src="https://github.com/user-attachments/assets/25f25f76-16d3-4b5f-9b70-87625ad7396b" />

# License

本项目采用 MIT 许可证 - 详见 [MIT License](/LICENSE "MIT License") 文件
