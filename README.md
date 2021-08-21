# <p align="center">YiBanClockIn</p>

## 必要声明
- 如有`发热发烧`等症状，请立即停止使用本项目，认真实履行社会义务，及时进行健康申报.

- 本仓库发布的YiBanClockIn项目中涉及的任何脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断.

- 所有使用者在使用YiBanClockIn项目的任何部分时，需先遵守法律法规。对于一切使用不当所造成的后果，需自行承担.对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害.

- 如果任何单位或个人认为该项目可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关文件.

- 任何以任何方式查看此项目的人或直接或间接使用该YiBanClockIn项目的任何脚本的使用者都应仔细阅读此声明。本人保留随时更改或补充此免责声明的权利。一旦使用并复制了任何相关脚本或YiBanClockIn项目的规则，则视为您已接受此免责声明.

您必须在下载后的24小时内从计算机或手机中完全删除以上内容.

> 您使用或者复制了本仓库且本人制作的任何脚本，则视为`已接受`此声明，请仔细阅读



## 环境

[Python3](https://www.python.org/) >= 3.6.8

## Windows
略

## Linux
```bash
yum install git -y

git clone https://ghproxy.com/https://github.com/Mashiro2000/YiBanClockIn.git   # 国内git较慢，故添加代理前缀

cd YiBanClockIn

chmod 777 YiBan.py

vi config.py
```

### 配置信息
编辑 `config.py`

#### 管理员信息
```json
admin = {
    "pushGroup" :{
        "pushToken": "abcdefghijklmnopqrstuvwsyz",    # Push Plus Token
        "pushTopic": "777"  # Push Plus群组编码
    },
    "mail":{
        "sendMail": "123456789@qq.com", # 发送人邮箱 -非必要
        "authCode": "abcdefghijklmnop", # 发送人邮箱授权码[不是密码] -非必要
        "adminMail": "987654321@qq.com" # 管理员邮箱 -非必要
        "smtpServer": "smtp.qq.com",     # 对应邮箱服务的SMTP服务器，以QQ邮箱为例smtp.qq.com -非必要
        "port": "465"                   # 对应邮箱服务的端口,25端口[简单邮箱传输协议],465端口[安全的邮箱传输协议] -非必要
    }
}
```

#### 用户信息
```json
accounts = [
    {
        "account": "12345678910",       # 你的易班账号 -必要
        "password": "mypassword",       # 你的易班密码 -必要
        "remark": "hello",              # 备注 -非必要
        "mail": "123456789@qq.com",     # 通知邮箱 -非必要
        "pushToken": ""                 # Push Plus Token
    }
]
```

### 定时设定
```bash
# 注:以root账号登录Linux
crontab -e
3 14/2 * * * python3 /root/YiBanClockIn/YiBan.py
```
[crontab 帮助文档](https://www.runoob.com/w3cnote/linux-crontab-tasks.html)

### 数据来源
- 本项目的打卡数据来源是基于前一天的打卡数据

### 特别说明
- 本项目仅适用于闽江学院的学生，其它学校请自行抓包！
- 特别感谢舍友提供的账号进行测试！
