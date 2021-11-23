# <p align="center">YiBanClockIn</p>

## 免责声明
- 如有`发热发烧`等症状，请立即停止使用本项目，认真实履行社会义务，及时进行健康申报.

- 本仓库发布的YiBanClockIn项目中涉及的任何脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断.

- 所有使用者在使用YiBanClockIn项目的任何部分时，需先遵守法律法规。对于一切使用不当所造成的后果，需自行承担.对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害.

- 如果任何单位或个人认为该项目可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关文件.

- 任何以任何方式查看此项目的人或直接或间接使用该YiBanClockIn项目的任何脚本的使用者都应仔细阅读此声明。本人保留随时更改或补充此免责声明的权利。一旦使用并复制了任何相关脚本或YiBanClockIn项目的规则，则视为您已接受此免责声明.

您必须在下载后的24小时内从计算机或手机中完全删除以上内容.

> 您使用或者复制了本仓库且本人制作的任何脚本，则视为`已接受`此声明，请仔细阅读



## 环境

[Python3](https://www.python.org/) >= 3.6.8

### Windows部署
`略`

### Linux部署(以CentOS7为例)
```bash
yum update

yum install git python3 -y

git clone https://ghproxy.com/https://github.com/Mashiro2000/YiBanClockIn.git

cd YiBanClockIn

pip3 install -r requirements.txt

vi YiBan.toml

python3 AioYiBan.py
```

### 青龙拉库命令
```
ql repo https://github.com/Mashiro2000/YiBanClockIn.git "" "images|notify"
```

#### 青龙环境变量
```text
> 账号信息
名称:YbCookie
值:nickname=XXX;account=11111111111;password=thisISPassword;mail=2222222222@qq.com;
-----------------------------------------------------------------------------------
> 发送人邮箱
名称:sendMail
值:3333333333@qq.com       # 管理员邮箱
--------------------
> 邮箱授权码
名称: authCode
值:abcdrfghijkl            # 不是密码
--------------------
> SMTP服务器
名称: smtpServer
值:smtp.qq.com             # 以QQ邮箱为例:smtp.qq.com
--------------------
> 邮箱服务的端口
名称:port
值:465                     # 25端口(简单邮箱传输协议),465端口(安全的邮箱传输协议)
```

## 个人通知邮箱
感谢舍友[@QingYi202](https://github.com/QingYi202)提供的邮箱模板
### 效果图
![](https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/clockIn.jpg)
