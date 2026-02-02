# tg_checkin
一个用于进行自动机器人签到的程序
# 项目结构
```
tg_checkin/
├── bots.json //添加需要的机器人
├── checkin.session  //生成的session文件
├── main.py 
├── tg_config.json // 配置api_hash和api_id
|—— proxy.json //配置代理设置， enabled = false 默认关闭
|—— state.json //保存上次记录的定时结果，未触发，则再次进行签到
```
# 效果展示图
<img width="858" height="534" alt="image" src="https://github.com/user-attachments/assets/25f25f76-16d3-4b5f-9b70-87625ad7396b" />


# License
本项目采用 MIT 许可证 - 详见[MIT License](/LICENSE "MIT License")文件
