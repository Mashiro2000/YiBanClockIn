# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/12
# @Author  : 2984922017@qq.com
# @File    : config.py
# @Software: PyCharm

## 授权码获取,以QQ邮箱为例【https://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256】
## 推送优先级: 无配置 > 邮箱通知
## 全体推送 如有配置，打卡反馈均发送管理员，主要是方便管理员查看某个账户打卡异常
## 推送优先级: 无配置 > 邮箱管理员通知

## 账号配置模板，多账号以逗号隔开
## {
##     "account": "易班账号(必要)",
##     "password": "易班密码(必要)",
##     "remark": "备注(非必要)",
##     "mail": "通知邮箱(非必要)",
## },


## 管理员设置
admin = {
    "mail":{
        "sendMail": "",                 # 发送人邮箱
        "authCode": "",                 # 发送人邮箱授权码(不是密码)
        "adminMail": "",                # 收件人邮箱
        "smtpServer":"",                # 对应邮箱服务的SMTP服务器，以QQ邮箱为例:smtp.qq.com
        "port":""                       # 对应邮箱服务的端口,25端口(简单邮箱传输协议),465端口(安全的邮箱传输协议)
    }
}

## 账户设置
accounts = [
    {
        "account": "",
        "password": "",
        "remark": "",
        "mail": "",
    },
    {
        "account": "",
        "password": "",
        "remark": "",
        "mail": "",
    }
]
