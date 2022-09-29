# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/25
# @Author  : moe@miku39.fun
# @File    : AioYiBan.py
# @Software: PyCharm

"""
cron:  20,25 14 * * * AioYiBan.py
new Env('校本化打卡');
"""

import asyncio
import base64
import json
# 系统自带库
import os
import random
import re
import shlex
# 邮箱模组
import smtplib
import subprocess
import time
from email.mime.text import MIMEText
from email.utils import formataddr

# 第三方库
try:
    import tomli
except ModuleNotFoundError:
    print("缺少tomli依赖！尝试安装")
    subprocess.run(
        shlex.split("pip3 install tomli -i https://pypi.tuna.tsinghua.edu.cn/simple"),
        shell=True,
        text=True,
    )

try:
    import aiohttp
except ModuleNotFoundError:
    print("缺少aiohttp依赖！尝试安装")
    subprocess.run(
        shlex.split("pip3 install aiohttp -i https://pypi.tuna.tsinghua.edu.cn/simple"),
        shell=True,
        text=True,
    )

try:
    import requests
except ModuleNotFoundError:
    print("缺少requests依赖！尝试安装!")
    subprocess.run(
        shlex.split(
            "pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple"
        ),
        shell=True,
        text=True,
    )

try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
except ModuleNotFoundError:
    print("缺少pycryptodome依赖！尝试安装")
    subprocess.run(
        shlex.split(
            "pip3 install pycryptodome -i https://pypi.tuna.tsinghua.edu.cn/simple"
        ),
        shell=True,
        text=True,
    )

# 配信文件
try:
    # 导入失败是允许范围内，且不打印提示
    from notify import send

    isNotify = True
except ModuleNotFoundError:
    isNotify = False

# 调试模式(仅用于检测打卡请求)
DEBUG = False

# 全局变量
allMess = f"任务:校本化打卡\n时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n"


class AioYiBan:
    # 构造函数
    def __init__(self, dic: dict, admin: dict) -> None:
        self.CompletedTaskID = None
        self.dic = dic
        self.admin = admin
        self.mess = ''
        self.name = ''
        self.csrf = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba0123456789', 32))
        self.cookies = {}
        self.cookies.update({"csrf_token": self.csrf})

    # 获取用户名
    async def getName(self) -> None:
        if self.dic['nickname'] != "":
            self.name = self.dic['nickname']
        else:
            self.name = self.dic['account']

    # 个体邮件通知
    def notify(self, text: str, is_send: bool = True) -> None:
        self.mess += f"{self.name}\t{text}\n"
        if is_send is True:
            if all(self.admin.values()) and self.dic['mail']:
                self.sendMail(text)
            else:
                print(f"{self.name}\t管理员邮箱未配置或用户未提供邮箱，取消配信")

    # 密码加密
    async def encryptPassword(self, pwd: str) -> str:
        PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
            MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA6aTDM8BhCS8O0wlx2KzA
            Ajffez4G4A/QSnn1ZDuvLRbKBHm0vVBtBhD03QUnnHXvqigsOOwr4onUeNljegIC
            XC9h5exLFidQVB58MBjItMA81YVlZKBY9zth1neHeRTWlFTCx+WasvbS0HuYpF8+
            KPl7LJPjtI4XAAOLBntQGnPwCX2Ff/LgwqkZbOrHHkN444iLmViCXxNUDUMUR9bP
            A9/I5kwfyZ/mM5m8+IPhSXZ0f2uw1WLov1P4aeKkaaKCf5eL3n7/2vgq7kw2qSmR
            AGBZzW45PsjOEvygXFOy2n7AXL9nHogDiMdbe4aY2VT70sl0ccc4uvVOvVBMinOp
            d2rEpX0/8YE0dRXxukrM7i+r6lWy1lSKbP+0tQxQHNa/Cjg5W3uU+W9YmNUFc1w/
            7QT4SZrnRBEo++Xf9D3YNaOCFZXhy63IpY4eTQCJFQcXdnRbTXEdC3CtWNd7SV/h
            mfJYekb3GEV+10xLOvpe/+tCTeCDpFDJP6UuzLXBBADL2oV3D56hYlOlscjBokNU
            AYYlWgfwA91NjDsWW9mwapm/eLs4FNyH0JcMFTWH9dnl8B7PCUra/Lg/IVv6HkFE
            uCL7hVXGMbw2BZuCIC2VG1ZQ6QD64X8g5zL+HDsusQDbEJV2ZtojalTIjpxMksbR
            ZRsH+P3+NNOZOEwUdjJUAx8CAwEAAQ==
            -----END PUBLIC KEY-----'''
        cipher = PKCS1_v1_5.new(RSA.importKey(PUBLIC_KEY))
        cipher_text = base64.b64encode(cipher.encrypt(bytes(pwd, encoding="utf8")))
        return cipher_text.decode("utf-8")

    # AES填充模式
    def aes_pkcs7padding(self, data: bytes) -> bytes:
        bs = AES.block_size
        padding = bs - len(data) % bs
        padding_text = bytes(chr(padding) * padding, 'utf-8')
        return data + padding_text

    # AES加密
    def aes_encrypt(self, data: str) -> bytes:
        cipher = AES.new(bytes('2knV5VGRTScU7pOq', 'utf-8'), AES.MODE_CBC, bytes('UmNWaNtM0PUdtFCs', 'utf-8'))
        encrypted = base64.b64encode(cipher.encrypt(self.aes_pkcs7padding(bytes(data, 'utf-8'))))
        return base64.b64encode(encrypted)

    # 邮箱模板以及配信方法
    def sendMail(self, text: str) -> None:
        try:
            content = f"""
            <div style="width: 50%;float: left;visibility: hidden;">
                <p style="font-size: 1px;">UID:{self.name}</p>
            </div>
            <div style="width: 50%;float: left;visibility: hidden;">
                <p style="font-size: 1px;">打卡状态:{text}</p>
            </div>
            <div style="background:linear-gradient(to right,#cccc,white); width: 95%; max-width: 800px; min-width: 320px;;margin: auto auto; border-radius: 5px; border:skyblue 2px solid; overflow: hidden; -webkit-box-shadow: 0 0 20px 0 rgba(0, 0, 0, 0.12); box-shadow: 0 0 20px 0 rgba(0, 0, 0, 0.18); font-family : YouYuan,emoji;">
                <header style="overflow: hidden;position: relative;">
                    <div style="width: 100%;height: 100%;max-height:40%;box-shadow: 5px 5px 3px rgba(131, 89, 89, 0.3);text-align: center;">
                        <img style="width:100%;z-index: 666;height: 100%;" src="https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/aml.png" alt="">
                    </div>
                </header>
                <div style="position: relative;">
                    <img src="https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/rll.gif" alt="" style="width:20px;position: absolute;top: 0;right: 20px;">
                    <p style="position: relative;color: white;float: left;z-index: 999;background: #7c7676;padding: 5px 30px;margin: -25px auto 0 ;box-shadow: 5px 5px 5px rgba(0, 0, 0, 0.30)">Arknights</p>
                </div><br />
                <div style="border-bottom: 3px solid rgb(116, 116, 243);margin-top: 5px;"></div>
                <p style="position: relative;color: white;background:#7c7676;padding: 5px 10px;margin: 15px auto 0 ;">泰拉瑞亚是冒险之地！是神秘之地！是可让你塑造、捍卫、享受的大地。在泰拉瑞亚，你有无穷选择。手指发痒的动作游戏迷？建筑大师？收藏家？探险家？每个人都能找到自己想要的。</p>
                <div style="float:left; width:50%;margin-top: 19px;">
                    <img src="https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/skd.png" alt="" style="border-radius: 30px;width: 100%;">
                    <div></div>
                    <p style="text-align: center;color:skyblue;font-weight: 700;font-size: 15px;">博士,“随我走吧，回到我们永恒的故乡。” </p>
                    <div style="width: 100%;">
                        <span style="font-size: 20px; color: black;text-shadow: 1px 1px 1px #f35e31;width: 50%;">Date：</span>{time.strftime('%Y-%m-%d', time.localtime())}
                    </div>
                    <div><span style="font-size: 20px; color:black;text-shadow: 1px 1px 1px #f35e31;width: 50%;">Time：</span>{time.strftime('%H:%M:%S', time.localtime())}</div>
                </div>
                <div style="width: 45%;float: right;margin-top: 19px;">
                    <span  style="font-weight: 700;">刀客塔今日课题：</span><br />
                    <span>UID:<span
                            style="text-decoration: none;color: orange;text-align: left;">{self.name}</span> <br />状态:<span style="text-decoration: none;color: orange ">{text}</span></span>
                    <div style="margin-top: 12px;">
                        <img src="https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/a1.jpg" alt="" style="width: 45%; max-width: 100px;border-top-left-radius: 40px;">
                        <img src="https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/a2.jpg" alt="" style="width:45%; max-width: 100px;border-top-right-radius: 40px;"><br/>
                        <img src="https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/a3.jpg" alt="" style="width:45%; max-width: 100px;border-bottom-left-radius: 40px;">
                        <img src="https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/a4.jpg" alt="" style="width: 45%; max-width: 100px;border-bottom-right-radius: 40px;">
                    </div>
                </div>
            </div>
            <div style="clear:both;margin-bottom: 10px;"></div>
            <div style="text-align: center;"><img src="https://cdn.jsdelivr.net/gh/Mashiro2000/YiBanClockIn@main/images/233.jpg" alt="" style="width: 90%;"></div>
            <p style="font-size: 12px;text-align: center;color: #999;">本邮件由可露希尔酱发出。<br />
                Copyright &copy; 2022 <a style="text-decoration:none; color: #6cf;" target="_blank" href="https://github.com/Mashiro2000/YiBanClockIn">Mashiro2000</a> Rhode Island</p>
                    """
            msg = MIMEText(content, 'html', 'utf-8')
            msg['From'] = formataddr(("no-reply", self.admin['sendMail']))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr((self.name, self.dic['mail']))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "易班打卡通知"  # 邮件的主题，也可以说是标题
            server = smtplib.SMTP_SSL(self.admin['smtpServer'], int(self.admin['port']))  # 发件人邮箱中的SMTP服务器，端口
            server.login(self.admin['sendMail'], self.admin['authCode'])  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.admin['sendMail'], [self.dic['mail']], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()
            return print(f"{self.name}\t信件发送成功！\n")
        except Exception as error:
            return print(f"{self.name}\t邮件发送失败!\t失败原因:{error}\n")

    async def joinCookie(self, aioResponse) -> None:
        for i in aioResponse.cookies.values():
            ckList = re.findall(r'Set-Cookie: (.*?);', str(i), re.S)[0].split('=')
            self.cookies.update({ckList[0]: ckList[-1]})

    async def login(self) -> bool:
        '''
        url = "https://mobile.yiban.cn/api/v4/passport/login"
        header= {
            'Origin': 'https://mobile.yiban.cn',
            'User-Agent': 'YiBan/5.0.4 Mozilla/5.0 (Linux; Android 7.1.2; V1938T Build/N2G48C; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Safari/537.36',
            'Referer': 'https://mobile.yiban.cn',
            'AppVersion': '5.0.4'
        }
        data = {
            "device": "HUAWEI",
            "v": "5.0.4",
            "mobile":int(self.dic['account']),
            "password": await self.encryptPassword(self.dic['password']),
            "token": "",
            "ct": "2",
            "identify": "0",
            "sversion": "25",
            "app": "1",
            "apn": "wifi",
            "authCode": "",
            "sig": "934932a8993b5e23"
        }'''
        # 登录接口取自于: https://github.com/Sricor/yiban/blob/main/yiban/Core/Login.py#L68
        url = "https://www.yiban.cn/login/doLoginAjax"
        header = {
            "User-Agent": "Yiban",
            "AppVersion": "5.0.12"
        }
        data = {
            'account': self.dic['account'],
            'password': self.dic['password']
        }
        async with self.sess.post(url=url, data=data, headers=header) as aioResponse:
            response = await aioResponse.json()
            await self.joinCookie(aioResponse)
            if response['code'] == 200:
                self.access_token = self.cookies.get('yiban_user_token')
                await asyncio.sleep(0.1)
                return True
            else:
                self.notify(f"登录失败", is_send=False)
                return False

    async def getAuthUrl(self) -> None:
        url = 'http://f.yiban.cn/iframe/index'
        params = {
            "act": "iapp7463"
        }
        header = {
            "yiban_user_token": self.access_token
        }
        cookies = {'yiban_user_token': self.access_token}
        async with self.sess.get(url=url, params=params, headers=header, cookies=cookies,
                                       allow_redirects=False) as aioResponse:
            await self.joinCookie(aioResponse)
            self.verify = aioResponse.headers.get('Location')
            self.verify_request = re.findall(r"verify_request=(.*?)&", str(self.verify))[0]

    async def auth(self) -> None:
        url = "https://api.uyiban.com/base/c/auth/yiban"
        self.sess.headers.update({
            'origin': 'https://app.uyiban.com',
            'referer': 'https://app.uyiban.com/',
            'Host': 'api.uyiban.com',
            'user-agent': 'yiban'
        })
        params = {
            "verifyRequest": self.verify_request,
            "CSRF": self.csrf
        }
        async with self.sess.get(url=url, params=params) as aioResponse:
            await aioResponse.json(content_type='text/html', encoding='utf-8')
            await self.joinCookie(aioResponse)
            await asyncio.sleep(0.1)

    async def authYiBan(self) -> bool:
        url = 'https://oauth.yiban.cn/code/usersure'
        headers = {
            "Host": "oauth.yiban.cn",
            "Origin": "https://oauth.yiban.cn",
            "Referer": "https://oauth.yiban.cn/code/html?client_id=95626fa3080300ea&redirect_uri=https://f.yiban.cn/iapp7463",
            "User-Agent": "yiban"
        }
        data = {
            'client_id': '95626fa3080300ea',
            'redirect_uri': 'https://f.yiban.cn/iapp7463',
            'state': '',
            'scope': '1,2,3,4,',
            'display': 'html'
        }
        async with self.sess.post(url=url, headers=headers, data=data) as aioResponse:
            await self.joinCookie(aioResponse)
            await asyncio.sleep(0.1)
            await aioResponse.json(content_type='text/html', encoding='utf-8')
            if aioResponse.status == 200:
                await self.runFun()
                return True
            else:
                return False

    async def CompletedList(self) -> bool:
        yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        url = f"https://api.uyiban.com/officeTask/client/index/completedList"
        params = {
            'StartTime': f"{yesterday} 00:00",
            'EndTime': f"{today} 23:00",
            'CSRF': self.csrf
        }
        async with self.sess.get(url=url, params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html', encoding='utf-8')
            await self.joinCookie(aioResponse)
            await asyncio.sleep(0.1)
            if response['code'] == 0:
                if len(response['data']) > 0:
                    for sub in response['data']:
                        if sub['Title'] == f"学生每日健康打卡({today}）":
                            if not DEBUG:
                                if self.admin.get('repeat', False) == 'true':
                                    self.notify(f"今日已打卡")
                                else:
                                    self.notify(f"今日已打卡", is_send=False)
                                return False
                            else:
                                self.CompletedTaskID = sub['TaskId']
                                return True
                    else:
                        dic = [content for content in response['data'] if
                               re.findall(f"学生每日健康打卡\({yesterday}）", content['Title'])]
                        if len(dic) == 1:
                            self.CompletedTaskID = dic[0]['TaskId']
                            return True
                        else:
                            self.notify(f"账号:{self.name}\t存在多个已完成任务且筛选失败，故取消打卡")
                            return False
                elif len(response['data']) == 0:
                    self.notify(f"昨日无打卡任务，历史数据调用失败")
                    return False
            elif response['code'] == 999:
                if await self.authYiBan() is True:
                    return False
                else:
                    self.notify(f"易班授权已过期，尝试授权失败!")
            else:
                self.notify(f"出现错误，原因:{response}")
                return False

    async def getInitiateId(self) -> None:
        url = f"https://api.uyiban.com/officeTask/client/index/detail"
        params = {
            "TaskId": self.CompletedTaskID,
            "CSRF": self.csrf
        }
        async with self.sess.get(url=url, params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html', encoding='utf-8')
            await self.joinCookie(aioResponse)
            self.InitiateId = response['data']['InitiateId']
            await asyncio.sleep(0.1)

    async def getClockInMess(self) -> None:
        url = f"https://api.uyiban.com/workFlow/c/work/show/view/{self.InitiateId}"
        params = {
            "CSRF": self.csrf
        }
        async with self.sess.get(url=url, params=params) as aioResponse:
            self.result = await aioResponse.json(content_type='text/html', encoding='utf-8')
            await self.joinCookie(aioResponse)
            await asyncio.sleep(0.1)

    async def unCompletedList(self) -> bool:
        if DEBUG is True:
            self.unCompletedTaskID = self.CompletedTaskID
            return True
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        url = f"https://api.uyiban.com/officeTask/client/index/uncompletedList"
        params = {
            'Title': '学生每日健康打卡',
            'StartTime': f"{today} 00:00",
            'EndTime': f"{today} 23:00",
            'CSRF': self.csrf
        }
        async with self.sess.get(url=url, params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html', encoding='utf-8')
            await self.joinCookie(aioResponse)
            await asyncio.sleep(0.1)
            if response['code'] == 0:
                if len(response['data']) == 1:
                    self.unCompletedTaskID = response['data'][0]['TaskId']
                    return True
                elif len(response['data']) == 0:
                    self.notify(f"任务未发布，故不继续执行！")
                    return False
                elif len(response['data']) > 1:
                    dic = [content for content in response['data'] if
                           re.findall(f"学生每日健康打卡\({today}）", content['Title']) != []]
                    if len(dic) == 1:
                        self.unCompletedTaskID = dic[0]['TaskId']
                        return True
                    else:
                        self.notify(f"存在多个未完成的任务且筛选失败，故不进行打卡！")
                        return False
            else:
                self.notify(f"未知错误，原因:{response['message']}")
                return False

    async def getWFId(self) -> bool:
        url = f"https://api.uyiban.com/officeTask/client/index/detail"
        params = {
            "TaskId": self.unCompletedTaskID,
            "CSRF": self.csrf
        }
        async with self.sess.get(url=url, params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html', encoding='utf-8')
            await self.joinCookie(aioResponse)
            await asyncio.sleep(0.1)
            if round(time.time()) > response['data']['StartTime']:
                self.WFId = response['data']['WFId']
                self.title = response['data']['Title']
                return True
            else:
                self.notify(f"未到打卡时间！")
                return False

    async def isUpdate(self) -> bool:
        url = f"https://api.uyiban.com/workFlow/c/my/form/{self.WFId}"
        params = {
            "CSRF": self.csrf
        }
        async with self.sess.get(url=url, params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html', encoding='utf-8')
            await self.joinCookie(aioResponse)
            if response['data']['Id'] == self.result['data']['Initiate']['WFId']:
                await asyncio.sleep(0.1)
                return True
            else:
                self.notify(f"打卡内容已更新，请手动打卡！")
                return False

    async def formatDate(self) -> None:
        formDataJson = self.result['data']['Initiate']['FormDataJson']
        self.formDataJson = {each['id']: each['value'] for each in formDataJson}
        for each in self.formDataJson:
            if type(self.formDataJson[each]) is dict and self.formDataJson[each].get('time'):
                self.formDataJson[each]['time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime())
        self.extendDataJson = self.result['data']['Initiate']['ExtendDataJson']
        self.extendDataJson['TaskId'] = self.unCompletedTaskID
        self.extendDataJson['content'][0]['value'] = self.title

    async def clockIn(self) -> None:
        url = "https://api.uyiban.com/workFlow/c/my/apply/"
        headers = {
            'origin': 'https://app.uyiban.com',
            'referer': 'https://app.uyiban.com/',
            'Host': 'api.uyiban.com',
            'user-agent': 'yiban'
        }
        params = {
            "CSRF": self.csrf
        }
        postData = {
            'WFId': self.WFId,
            'Data': json.dumps(self.formDataJson, ensure_ascii=False),
            "Extend": json.dumps(self.extendDataJson, ensure_ascii=False)
        }
        data = {
            'Str': self.aes_encrypt(json.dumps(postData, ensure_ascii=False))
        }
        response = requests.post(url=url, headers=headers, params=params, data=data, cookies=self.cookies).json()
        if response['code'] == 0:
            self.notify(f"打卡成功!")
        else:
            self.notify(f"未知错误，原因:{response['msg']}")

    async def tryLogin(self) -> bool:
        if self.dic['account'] != '' and self.dic['password'] != '':
            for _ in range(3):
                try:
                    await asyncio.sleep(random.randint(2, 5))  # 随机延时
                    if await self.login():
                        return True
                except:
                    continue
            else:
                self.notify(f"多次请求失败，暂不打卡！")
                return False

    async def runFun(self) -> None:
        await self.getAuthUrl()
        await self.auth()
        if await self.CompletedList():
            await self.getInitiateId()
            await self.getClockInMess()
            if await self.unCompletedList():
                if await self.getWFId():
                    if await self.isUpdate():
                        await self.formatDate()
                        await self.clockIn()
        self.mess += ('*' * 40 + '\n' * 4)

    async def run(self):
        global allMess
        await self.getName()
        if await self.tryLogin():
            await self.runFun()
        allMess += self.mess

    async def start(self):
        async with aiohttp.ClientSession(cookies={"csrf_token": self.csrf}) as self.sess:
            await self.run()


def readToml() -> dict:
    tomlFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'YiBan.toml')
    try:
        if os.path.exists(tomlFile):
            # if dic := tomli.load(open(tomlFile,'rb')):   # 3.8.0版本写法
            dic = tomli.load(open(tomlFile, 'rb'))  # 3.6.8版本写法
            if dic:
                return dic
        else:
            return {}
    except Exception as error:
        print(f"toml文件数据导入失败，失败原因:{error}")


def accountEnv() -> list:
    accounts = []
    cookieRegex = re.compile(
        r'nickname=(?P<nickname>.*?);account=(?P<account>.*?);password=(?P<password>.*?);mail=(?P<mail>.*?);', re.S)
    # if string:=os.getenv(('YbCookie')):   # 3.8.0版本写法
    string = os.getenv(('YbCookie'))  # 3.6.8版本写法
    if string:
        for each in string.split('&'):
            for each in re.finditer(cookieRegex, each):
                accounts.append({
                    'nickname': each.group('nickname'),
                    'account': each.group('account'),
                    'password': each.group('password'),
                    'mail': each.group('mail')
                })
    return accounts


def adminEnv() -> dict:
    dic = {}
    # 3.8.0版本写法
    # if sendMail:=os.getenv('sendMail'):
    #     dic['sendMail'] = sendMail
    # if authCode:=os.getenv('authCode'):
    #     dic['authCode'] = authCode
    # if smtpServer:=os.getenv('smtpServer'):
    #     dic['smtpServer'] = smtpServer
    # if port:=os.getenv('port'):
    #     dic['port'] = port
    # if repeat:=os.getenv('repeat'):
    #     dic['repeat'] = repeat
    # 3.6.8版本写法
    sendMail = os.getenv('sendMail')
    if sendMail:
        dic['sendMail'] = sendMail
    authCode = os.getenv('authCode')
    if authCode:
        dic['authCode'] = authCode
    smtpServer = os.getenv('smtpServer')
    if smtpServer:
        dic['smtpServer'] = smtpServer
    port = os.getenv('port')
    if port:
        dic['port'] = port
    repeat = os.getenv('repeat')
    if repeat:
        dic['repeat'] = repeat
    if dic != {}:
        if all(dic.values()):
            return dic


async def asyncMain() -> None:
    account = []  # 提前声明账号列表，如若配置文件不存在，也有现成列表可供追加
    admin = {}  # 提前声明账号列表，如若配置文件和环境变量均不存在，也应提供一个空字典
    # 3.8.0版本写法
    # if data := readToml():              # 读取配置文件中的account以及admin字段
    #     account = data['account']
    #     admin = data['admin']
    # if data := accountEnv():            # 如果环境变量存在账号密码，则追加到账号列表
    #     account.extend(data)
    # if data:=adminEnv():                # 如果环境变量存在邮箱参数，则替换，环境变量优先级高于配置文件
    #     admin = data
    # 3.6.8版本写法
    data = readToml()
    if data:
        account = data['account']
        admin = data['admin']
    data = accountEnv()
    if data:
        account.extend(data)
    data = adminEnv()
    if data:
        admin = data
    if account:
        # 3.8.0版本写法
        # tasks = [asyncio.create_task(AioYiBan(each,admin).start()) for each in account if each]
        # 3.6.8版本写法
        tasks = [asyncio.ensure_future(AioYiBan(each, admin).start()) for each in account if each]
        await asyncio.wait(tasks, timeout=None)
    else:
        print("配置文件与环境变量均无易班账号，取消执行")


def main_handler(event, context) -> None:
    global allMess
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncMain())
    if isNotify is True:
        send('易班校本化打卡', allMess)
    else:
        print(allMess)


def main() -> None:
    main_handler(None, None)


if __name__ == '__main__':
    main()
