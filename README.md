# YiBanClockIn

## 环境

- [Python3](https://www.python.org/) >= 3.6.8

## Windows
略

## Linux
```bash
git clone https://github.com/Mashiro2000/YiBanClockIn.git

cd YiBanClockIn

vi config.py
```

### 配置信息
Edit `config.json`:

#### 管理员信息
```json
admin = {
    "pushGroup" :{
        "pushToken": "",    # Push Plus Token -非必要
        "pushTopic": ""     # Push Plus群组编码 -非必要
    },
    "mail":{
        "name": "no-reply",             发件人昵称 -非必要
        "sendMail": "123456789@qq.com", 发送人邮箱 -非必要
        "authCode": "abcdefghijklmnop", 发送人邮箱授权码(不是密码) -非必要
        "smtpServer":"smtp.qq.com",     # 对应邮箱服务的SMTP服务器，以QQ邮箱为例:smtp.qq.com -非必要
        "port":"465"                    # 对应邮箱服务的端口,25端口(简单邮箱传输协议),465端口(安全的邮箱传输协议) -非必要
    }
}
```

#### 用户信息
```json
accounts = [
    {
        "account": "12345678910",    # 你的易班账号 -必要
        "password": "mypassword",    # 你的易班密码 -必要
        "remark": "hello",           # 备注 -非必要
        "mail": "123456789@qq.com",  # 通知邮箱 -非必要
        "pushToken":""              # Push Plus -非必要
    }
]
```

### 定时设定
```bash
pwd # 获取当前位置
crontab -e
1 14-18/2 * * * python3 当前目录/YiBan.py
