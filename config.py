# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/12
# @Author  : 2984922017@qq.com
# @File    : config.py
# @Software: PyCharm

## Push Plus发信平台
## 官方网站：http://www.pushplus.plus
## 下方填写您的Token，微信扫码登录后一对一推送或一对多推送下面的token

## 授权码获取,以QQ邮箱为例【https://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256】

## 个人推送
## 推送优先级: 无配置 > 邮箱通知 > Push一对一推送

## 全体推送 如有配置，打卡反馈均发送管理员(群组)，主要是方便管理员查看某个账户打卡异常
## 推送优先级: 无配置 > Push一对多推送 > 管理员邮箱通知

## 账号配置模板，多账号以逗号隔开
## {
##     "account": "易班账号(必要)",
##     "password": "易班密码(必要)",
##     "remark": "备注(非必要)",
##     "mail": "通知邮箱(非必要)",
##     "pushToken": "Push Plus Token(非必要)"
## },


## 日志文件存在路径
LOG_PATH = ""   # 非必要


## 管理员设置
admin = {
    "pushGroup" :{
        "pushToken": "",    # Push Plus Token
        "pushTopic": ""  # Push Plus群组编码
    },
    "mail":{
        "adminMail": "",   # 收件人邮箱
        "sendMail": "",     # 发送人邮箱
        "authCode": "",     # 发送人邮箱授权码(不是密码)
        "smtpServer":"smtp.qq.com",         # 对应邮箱服务的SMTP服务器，以QQ邮箱为例:smtp.qq.com
        "port":"465"                        # 对应邮箱服务的端口,25端口(简单邮箱传输协议),465端口(安全的邮箱传输协议)
    }
}


## 账户设置
accounts = [
    {
        "account": "",
        "password": "",
        "remark": "",
        "mail": "",
        "pushToken": ""
    },
    {
        "account": "",
        "password": "",
        "remark": "",
        "mail": "",
        "pushToken": ""
    }
]
