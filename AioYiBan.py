# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/12
# @Author  : MashiroF
# @File    : AioYiBan.py
# @Software: PyCharm

# 系统自带库
import os
import re
import json
import time
import base64
import random
import asyncio
import logging

# 邮箱模组
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# 第三方库
try:
    import requests
except ModuleNotFoundError:
    print("缺少requests依赖！程序将尝试安装依赖！")
    os.system("pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple")

try:
    import aiohttp
except ModuleNotFoundError:
    print("缺少aiohttp依赖！程序将尝试安装依赖！")
    os.system("pip3 install aiohttp -i https://pypi.tuna.tsinghua.edu.cn/simple")

try:
    from Crypto.Cipher import AES,PKCS1_v1_5
    from Crypto.PublicKey import RSA
except ModuleNotFoundError:
    print("缺少pycryptodome依赖！程序将尝试安装依赖！")
    os.system("pip3 install pycryptodome -i https://pypi.tuna.tsinghua.edu.cn/simple")

try:
    import toml
except ModuleNotFoundError:
    print("缺少toml依赖！程序将尝试安装依赖！")
    os.system("pip3 install toml -i https://pypi.tuna.tsinghua.edu.cn/simple")

# 日志模块
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logFormat = logging.Formatter("%(message)s")

# 配信文件
try:
    from sendNotify import send
    isNotify =True
except Exception as error:
    isNotify = False
    logger.info('推送文件有误')
    logger.info(f'失败原因:{error}')

# 全局变量
allMess = str()

class AioYiBan:
    def __init__(self,dic,admin):
        self.dic = dic
        self.admin = admin
        self.mess = str()
        self.name = str()
        self.csrf =''.join(random.sample('zyxwvutsrqponmlkjihgfedcba0123456789',32))
        self.cookies = dict()
        self.cookies.update({"csrf_token":self.csrf})

    def notify(self,text,isSend=True):
        self.mess += text + '\n'
        if isSend == True:
            self.sendMail(text)
        logger.info(text)

    async def getName(self):
        if self.dic['nickname'] != "":
            self.name = self.dic['nickname']
        else:
            self.name =  self.dic['account']

    async def encryptPassword(self, pwd):
        #密码加密
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

    def aes_pkcs7padding(self,data):
        bs = AES.block_size
        padding = bs - len(data) % bs
        padding_text = bytes(chr(padding) * padding, 'utf-8')
        return data + padding_text

    def aes_encrypt(self,data):
        cipher = AES.new(bytes('2knV5VGRTScU7pOq', 'utf-8'), AES.MODE_CBC, bytes('UmNWaNtM0PUdtFCs', 'utf-8'))
        encrypted = base64.b64encode(cipher.encrypt(self.aes_pkcs7padding(bytes(data, 'utf-8'))))
        return base64.b64encode(encrypted)

    def sendMail(self,text):
        try:
            content = f"""
             <div style="background: white; width:  800px; max-width: 800px; margin: auto auto; border-radius: 5px; border:skyblue 2px solid; overflow: hidden; -webkit-box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.12); box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.18); font-family : YouYuan;">
        <header style="overflow: hidden;position: relative;">
        <div style="width: 100%;height:100%;box-shadow: 5px 5px 3px rgba(131, 89, 89, 0.3);text-align:center;">
                <div style="text-align: center;position:absolute; z-index: 999;height: 500px;right:0">
                    <p style="color: #c6c6c6;font-weight: 700;font-size: 25px;writing-mode: tb-rl;">博士，您还有许多事情需要处理。现在还不能休息哦。</p>
                </div>
                <img style="width:100%;z-index: 666;height: 100%;box-shadow: 1px;" src="https://gitee.com/Mashiro2000/YiBanClockIn/raw/main/images/aml.png">
        </div>
        </header>
        <div style="padding: 5px 20px;position: relative;">
        <p style="position: relative;color: white;float: left;z-index: 999;background: #cccc;padding: 5px 30px;margin: -25px auto 0 ;box-shadow: 5px 5px 5px rgba(0, 0, 0, 0.30)">Arknights</p>
        <br>
        <h3>舰长:<font style="text-decoration: none;color: orange ">{self.name}</font>任务状态：<font style="text-decoration: none;color: orange ">{text}</font>！</h3>
        <img src="https://gitee.com/Mashiro2000/YiBanClockIn/raw/main/images/rl.png" alt="" style="width: 100px;position: absolute;top: 20px;right: 100px;">
        <h3>刀客塔今日课题：</h3>
        <div style="float:right;width: 50%;background-color:#eee ;margin:15px 0px;border: 1px solid skyblue rgba(0, 0, 0, 0.30);padding: 20px;">签到状态：status</a></div>
         <div style="float: left;">
            <img src="https://gitee.com/Mashiro2000/YiBanClockIn/raw/main/images/a1.jpg" alt="" style="width: 100%; max-width: 100px;">
            <img src="https://gitee.com/Mashiro2000/YiBanClockIn/raw/main/images/a2.jpg" alt="" style="width: 100%; max-width: 100px;">
            <div></div>
            <img src="https://gitee.com/Mashiro2000/YiBanClockIn/raw/main/images/a3.jpg" alt="" style="width: 100%; max-width: 100px;">
            <img src="https://gitee.com/Mashiro2000/YiBanClockIn/raw/main/images/a4.jpg" alt="" style="width: 100%; max-width: 100px;">
        </div>
       <div style="clear:both"></div>
        <p style="font-size: 12px;text-align: center;color: #999;">本邮件由可露希尔酱发出。<br>
        Copyright &copy; 2021 <a style="text-decoration:none; color: #66ccff;" target="_blank" href="https://github.com/Mashiro2000/YiBanClockIn">Mashiro2000</a> Rhode Island</p>
        </div>"""
            msg= MIMEText(content, 'html', 'utf-8')
            msg['From']=formataddr(["no-reply",self.admin['sendMail']])                 # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr([self.name,self.dic['mail']])                          # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "易班打卡通知"                                               # 邮件的主题，也可以说是标题
            server=smtplib.SMTP_SSL(self.admin['smtpServer'], int(self.admin['port']))  # 发件人邮箱中的SMTP服务器，端口
            server.login(self.admin['sendMail'], self.admin['authCode'])                # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.admin['sendMail'],[self.dic['mail']],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()
            return print(f"{self.name}\t信件发送成功！\n")
        except Exception as error:
            return print(f"{self.name}\t邮件发送失败!\t失败原因:{error}\n")

    async def joinCookie(self,aioResponse):
        for i in aioResponse.cookies.values():
            ckList = re.findall(r'Set-Cookie: (.*?);',str(i),re.S)[0].split('=')
            self.cookies.update({ckList[0]: ckList[-1]})

    async def login(self):
        url = "https://mobile.yiban.cn/api/v4/passport/login"
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
        }
        header= {
            'Origin': 'https://mobile.yiban.cn',
            'User-Agent': 'YiBan/5.0.4 Mozilla/5.0 (Linux; Android 7.1.2; V1938T Build/N2G48C; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Safari/537.36',
            'Referer': 'https://mobile.yiban.cn',
            'AppVersion': '5.0.4'
        }
        async with await self.sess.post(url=url, data=data, headers=header) as aioResponse:
            response = await aioResponse.json()
            await self.joinCookie(aioResponse)
            if response['response'] == 100:
                self.access_token = response['data']['access_token']
                await asyncio.sleep(0.1)
                return True
            else:
                self.notify(f"登录失败")
                return False

    async def getAuthUrl(self):
        url = "https://f.yiban.cn/iapp/index"
        params = {
            "act":"iapp7463"
        }
        header = {
            "authorization": f"Bearer {self.access_token}",
            "logintoken": self.access_token
        }
        async with await self.sess.get(url=f"https://f.yiban.cn/iapp7463",headers=header,allow_redirects=False) as aioResponse1:
            await aioResponse1.text()
            await self.joinCookie(aioResponse1)
            await asyncio.sleep(0.1)
            async with await self.sess.get(url=url,params=params,headers=header,allow_redirects=False) as aioResponse2:
                self.verify = aioResponse2.headers['Location']
                await self.joinCookie(aioResponse2)
                self.verify_request = re.findall(r"verify_request=(.*?)&", self.verify)[0]
            await asyncio.sleep(0.1)

    async def auth(self):
        url = "https://api.uyiban.com/base/c/auth/yiban"
        self.sess.headers.update({
            'origin': 'https://app.uyiban.com',
            'referer': 'https://app.uyiban.com/',
            'Host': 'api.uyiban.com',
            'user-agent': 'yiban'
        })
        params = {
            "verifyRequest":self.verify_request,
            "CSRF":self.csrf
        }
        async with await self.sess.get(url=url, params=params) as aioResponse:
            await aioResponse.read()
            await self.joinCookie(aioResponse)
        await asyncio.sleep(0.1)

    async def CompletedList(self):
        yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        url = f"https://api.uyiban.com/officeTask/client/index/completedList?StartTime={yesterday}%2000%3A00&EndTime={today}%2023%3A59&CSRF={self.csrf}"
        async with await self.sess.get(url=url) as aioResponse:
            response = await aioResponse.json(content_type='text/html',encoding='utf-8')
            await self.joinCookie(aioResponse)
        if response['code'] == 0:
                if len(response['data']) > 0:
                    for sub in response['data']:
                        if sub['Title'] == f"学生每日健康打卡({time.strftime('%Y-%m-%d', time.localtime())}）":
                            self.notify(f"今日已打卡")
                            return False
                    else:
                        dic = [content for content in response['data'] if re.findall(f"学生每日健康打卡\({time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))}）",content['Title']) !=[]]
                        if len(dic) == 1:
                            self.CompletedTaskID  = dic[0]['TaskId']
                            await asyncio.sleep(0.1)
                            return True
                        else:
                            self.notify(f"账号:{self.name}\t存在多个已完成任务且筛选失败，故取消打卡")
                            return False
                elif len(response['data']) == 0:
                    self.notify(f"昨日无打卡任务，历史数据调用失败")
                    return False
                elif response['code'] == 999:
                    self.notify(f"校本化授权已过期")
                    return False

    async def getInitiateId(self):
        url = f"https://api.uyiban.com/officeTask/client/index/detail"
        params = {
            "TaskId":self.CompletedTaskID,
            "CSRF": self.csrf
        }
        async with await self.sess.get(url=url,params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html',encoding='utf-8')
            await self.joinCookie(aioResponse)
        self.InitiateId = response['data']['InitiateId']
        await asyncio.sleep(0.1)

    async def getClockInMess(self):
        url = f"https://api.uyiban.com/workFlow/c/work/show/view/{self.InitiateId}"
        params = {
            "CSRF": self.csrf
        }
        async with await self.sess.get(url=url,params=params) as aioResponse:
            self.result = await aioResponse.json(content_type='text/html',encoding='utf-8')
            await self.joinCookie(aioResponse)
        await asyncio.sleep(0.1)

    async def unCompletedList(self):
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        url = f"https://api.uyiban.com/officeTask/client/index/uncompletedList"
        params = {
            'Title': '学生每日健康打卡',
            'StartTime': f"{today} 00:00",
            'EndTime': f"{today} 23:00",
            'CSRF': self.csrf
        }
        async with await self.sess.get(url=url,params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html',encoding='utf-8')
            await self.joinCookie(aioResponse)
            if response['code'] == 0:
                if len(response['data']) == 1:
                    self.unCompletedTaskID = response['data'][0]['TaskId']
                    await asyncio.sleep(0.1)
                    return True
                elif len(response['data']) == 0:
                    self.notify(f"任务未发布，故不继续执行！")
                    return False
                elif len(response['data']) > 1:
                    dic = [content for content in response['data'] if re.findall(f"学生每日健康打卡\({time.strftime('%Y-%m-%d', time.localtime(time.time()))}）",content['Title']) !=[]]
                    if len(dic) == 1:
                        self.unCompletedTaskID  = dic[0]['TaskId']
                        await asyncio.sleep(0.1)
                        return True
                    else:
                        self.notify(f"存在多个未完成的任务且筛选失败，故不进行打卡！")
                        return False
            else:
                self.notify(f"未知错误，原因:{response['message']}")
                return False

    async def getWFId(self):
        url = f"https://api.uyiban.com/officeTask/client/index/detail"
        params = {
            "TaskId":self.unCompletedTaskID,
            "CSRF": self.csrf
        }
        async with await self.sess.get(url=url,params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html',encoding='utf-8')
            await self.joinCookie(aioResponse)
            if round(time.time()) > response['data']['StartTime']:
                self.WFId = response['data']['WFId']
                self.title = response['data']['Title']
                await asyncio.sleep(0.1)
                return True
            else:
                self.notify(f"未到打卡时间！")
                return False

    async def isUpdate(self):
        url = f"https://api.uyiban.com/workFlow/c/my/form/{self.WFId}"
        params = {
            "CSRF":self.csrf
        }
        async with await self.sess.get(url=url,params=params) as aioResponse:
            response = await aioResponse.json(content_type='text/html',encoding='utf-8')
            await self.joinCookie(aioResponse)
            if response['data']['Id'] == self.result['data']['Initiate']['WFId']:
                await asyncio.sleep(0.1)
                return True
            else:
                self.notify(f"打卡内容已更新，请手动打卡！")
                return False

    async def formatDate(self):
        formDataJson = self.result['data']['Initiate']['FormDataJson']
        self.formDataJson = {each['id']: each['value'] for each in formDataJson}
        for each in self.formDataJson:
            if type(self.formDataJson[each]) is dict and self.formDataJson[each].get('time'):
                self.formDataJson[each]['time'] = time.strftime('%Y-%m-%d %H:%M',time.localtime())
        self.extendDataJson = {
            "TaskId":self.unCompletedTaskID,
            "title":self.result['data']['Initiate']['ExtendDataJson']['title'],
            "content":[
                {"label":self.result['data']['Initiate']['ExtendDataJson']['content'][0]['label'],"value":self.title},
                {"label":self.result['data']['Initiate']['ExtendDataJson']['content'][1]['label'],"value":self.result['data']['Initiate']['ExtendDataJson']['content'][1]['value']}]
        }

    async def clockIn(self):
        url = "https://api.uyiban.com/workFlow/c/my/apply/"
        headers = {
            'origin': 'https://app.uyiban.com',
            'referer': 'https://app.uyiban.com/',
            'Host': 'api.uyiban.com',
            'user-agent': 'yiban'
        }
        params = {
            "CSRF":self.csrf
        }
        postData= {
            'WFId':self.WFId,
            'Data' :json.dumps(self.formDataJson,ensure_ascii=False),
            "Extend":json.dumps(self.extendDataJson,ensure_ascii=False)
        }
        data = {
            'Str': self.aes_encrypt(json.dumps(postData, ensure_ascii=False))
        }
        response = requests.post(url=url,headers=headers,params=params,data=data,cookies=self.cookies).json()
        if response['code'] == 0:
            self.notify(f"打卡成功!")
        else:
            self.notify(f"未知错误，原因:{response['msg']}")

    async def tryLogin(self):
        if self.dic['account'] != '' and self.dic['password'] != '':
            for count in range(3):
                try:
                    await asyncio.sleep(random.randint(2,5))    # 随机延时
                    if await self.login():
                        return True
                except Exception as error:
                    self.notify(error)
            else:
                self.notify(f"多次请求失败，暂不打卡！")
                return False

    async def run(self):
        global allMess
        await self.getName()
        if await self.tryLogin():
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
            self.notify('*'*40 + '\n'*4,isSend=False)
        allMess += self.mess

    async def start(self):
        async with aiohttp.ClientSession(cookies={"csrf_token":self.csrf}) as self.sess:
            await self.run()

def readToml():
    try:
        if os.path.exists('YiBan.toml'):
            with open(file='YiBan.toml', mode='r') as f:
                if dic := toml.load(f):
                    return dic
        else:
            return dict({'account':list(),'admin':None})
    except Exception as error:
        print(f"toml文件数据导入失败，失败原因:{error}")

def accountEnv():
    accounts = []
    cookieRegex = re.compile(r'nickname=(?P<nickname>.*?);account=(?P<account>.*?);password=(?P<password>.*?);mail=(?P<mail>.*?);',re.S)
    if string:=os.getenv(('YbCookie')):
        for each in string.split('&'):
            for each in re.finditer(cookieRegex,each):
                if (nickname:=each.group('nickname')) and (phone:=each.group('phone')) and (passwd:=each.group('passwd')) and (mail:=each.group('mail')):
                    accounts.append({
                        'nickname': nickname,
                        'account': phone,
                        'password': passwd,
                        'mail': mail
                    })
    return accounts

def adminEnv():
    dic = {}
    if sendMail:=os.getenv('sendMail'):
        dic['sendMail'] = sendMail
    if authCode:=os.getenv('authCode'):
        dic['authCode'] = authCode
    if smtpServer:=os.getenv('smtpServer'):
        dic['smtpServer'] = smtpServer
    if port:=os.getenv('port'):
        dic['port'] = port
    if dic != {}:
        if all(dic.values()):
            return dic
    else:
        return False


async def asyncMain():
    if data := readToml():
        account = data['account']
        account.extend(accountEnv())
        if admin:=adminEnv() != False:
            data['admin'] = admin
        if account:
            tasks = [asyncio.create_task(AioYiBan(each,data['admin']).start()) for each in account if each]
            await asyncio.wait(tasks,timeout=None)
        else:
            logger.info("配置文件与环境变量均无易班账号，取消执行")

def main() -> None:
    global allMess
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncMain())
    print(allMess)
    send('易班校本化打卡',allMess)

if __name__ == '__main__':
    main()
