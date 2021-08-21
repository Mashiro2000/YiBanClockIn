# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/12
# @Author  : 2984922017@qq.com
# @File    : YiBan.py
# @Software: PyCharm

# 系统自带库
import os
import re
import sys
import json
import time
import base64
import random

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
    os.execl(sys.executable, 'python3', __file__, *sys.argv)

try:
    from Crypto.Cipher import PKCS1_v1_5
    from Crypto.PublicKey import RSA
except ModuleNotFoundError:
    print("缺少pycryptodome依赖！程序将尝试安装依赖！")
    os.system("pip3 install pycryptodome -i https://pypi.tuna.tsinghua.edu.cn/simple")
    os.execl(sys.executable, 'python3', __file__, *sys.argv)

# 配置文件
from config import accounts ,admin

# 全局变量
allMsg = []

# 主程序根目录与运行日志
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_PATH, "run.log")

# 初始化执行语句
if os.path.exists(LOG_PATH):
    os.remove(LOG_PATH)
with open(file=LOG_PATH,mode="w",encoding="utf-8") as f:
    f.write(f"时间:{time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime())}\n")

class Notify:
    def __init__(self,admin,dic):
        self.admin = admin
        self.dic = dic

    def getName(self):
        if self.dic['remark'] != "":
            return self.dic['remark']
        else:
            return self.dic['account']

    def send(self,content,isNotify=True):
        string = ""
        for key,value in content.items():
            string = string + f"{key}: {value}\n"
        allMsg.append(content)
        if isNotify == True:
            if self.dic['mail'] != "":
                return self.sendMail(string)
            else:
                return Notify.log(f"{self.getName()}\t未配置个人通知方式，取消发送！\n")

    def sendMail(self,content):
        try:
            msg= MIMEText(content, 'plain', 'utf-8')
            msg['From']=formataddr(["no-reply",self.admin['mail']['sendMail']])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr([self.getName(),self.dic['mail']])     # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "易班打卡通知"                                    # 邮件的主题，也可以说是标题

            server=smtplib.SMTP_SSL(self.admin['mail']['smtpServer'], int(admin['mail']['port']))  # 发件人邮箱中的SMTP服务器，端口
            server.login(self.admin['mail']['sendMail'], self.admin['mail']['authCode'])  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.admin['mail']['sendMail'],[self.dic['mail']],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
            return Notify.log(f"{self.getName()}\t已配置个人通知方式，信件发送成功！\n")
        except Exception as error:
            return Notify.log(f"{self.getName()}\t已配置个人通知方式，邮件发送失败!\n失败原因:{error}\n")

    def sendPushPlus(self,content):
        url = 'http://www.pushplus.plus/send'
        headers = {"Content-Type":"application/json"}
        if self.dic['pushToken'] != "":
            data = json.dumps({
                "token": self.dic['pushToken'],
                "title":"易班打卡通知",
                "content":json.dumps(content),
                "template":"json"
            })
            response = requests.post(url=url,data=data,headers=headers).json()
            for key,value in content.items():
                return Notify.log(f"{key}:{value}")
            if response['code'] == 200:
                return Notify.log("Push Plus发信成功！\n")
            else:
                return Notify.log(f"Push Plus发信失败！\t失败原因:{response['msg']}")

    @staticmethod
    def log(content):
        with open(file=LOG_PATH,mode="a",encoding="utf-8") as f:
            f.write(content)
            print(content)

    @staticmethod
    def sendTotal(lists):
        if len([each for each in admin['pushGroup'].values() if each != ""]) == 2:
            return Notify.sendTotalByPush(lists)
        elif len([each for each in admin['mail'].values() if each !=""]) == 5:
            return Notify.sendTotalByMail(lists)
        else:
            return Notify.log("无配置全体通知方式，取消发信！")

    @staticmethod
    def sendTotalByPush(lists):
        if len(lists) != 0:
            content = ""
            for each in lists:
                for key,value in each.items():
                    content = content + f"{key}: {value}\n"
                content = content +"\n"
            Notify.log("\n执行结果:\n" + content)
            url = 'http://www.pushplus.plus/send'
            headers = {"Content-Type":"application/json"}
            if admin['pushGroup']['pushToken'] != "" and admin['pushGroup']['pushTopic'] != "":
                data = json.dumps({
                    "token": admin['pushGroup']['pushToken'],
                    "title":"易班打卡通知",
                    "content":content,
                    "template":"txt",
                    "topic":admin['pushGroup']['pushTopic']
                })
                response = requests.post(url=url,data=data,headers=headers).json()
                print(content)
                if response['code'] == 200:
                    Notify.log(f"Push Plus发信成功！")
                else:
                    Notify.log(f"Push Plus发信失败！\t失败原因:{response['msg']}")
                    
    @staticmethod
    def sendTotalByMail(lists):
        if len(lists) != 0:
            content = ""
            for each in lists:
                for key,value in each.items():
                    content = content + f"{key}: {value}\n"
                content = content +"\n"
            Notify.log("\n执行结果:\n" + content)
            try:
                msg= MIMEText(content, 'plain', 'utf-8')
                msg['From']=formataddr(["no-reply",admin['mail']['sendMail']])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
                msg['To']=formataddr(["admin",admin['mail']['adminMail']])     # 括号里的对应收件人邮箱昵称、收件人邮箱账号
                msg['Subject'] = "易班打卡通知"                                    # 邮件的主题，也可以说是标题

                server=smtplib.SMTP_SSL(admin['mail']['smtpServer'], int(admin['mail']['port']))  # 发件人邮箱中的SMTP服务器，端口
                server.login(admin['mail']['sendMail'], admin['mail']['authCode'])  # 括号中对应的是发件人邮箱账号、邮箱密码
                server.sendmail(admin['mail']['sendMail'],[admin['mail']['adminMail']],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
                server.quit()  # 关闭连接
                Notify.log(f"管理员信件发送成功！")
            except Exception as error:
                Notify.log(f"管理员邮件发送失败!\n失败原因:{error}")


class YiBan:
    def __init__(self,admin,dic):
        self.admin = admin
        self.dic = dic
        self.sess = requests.Session()
        self.csrf =''.join(random.sample('zyxwvutsrqponmlkjihgfedcba0123456789',32))
        self.sess.cookies.update({"csrf_token":self.csrf})
        self.notify = Notify(self.admin,self.dic)

    def getName(self):
        if self.dic['remark'] != "":
            return self.dic['remark']
        else:
            return self.dic['account']

    def encryptPassword(self, pwd):
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

    def login(self):
        url = "https://mobile.yiban.cn/api/v4/passport/login"
        param = {
            "device": "HUAWEI",
            "v": "5.0.1",
            "mobile":int(self.dic['account']),
            "password": self.encryptPassword(self.dic['password']),
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
            'User-Agent': 'YiBan/5.0.1 Mozilla/5.0 (Linux; Android 7.1.2; V1938T Build/N2G48C; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Safari/537.36',
            'Referer': 'https://mobile.yiban.cn',
            'AppVersion': '5.0.1'
        }
        response = self.sess.post(url=url, params=param, headers=header).json()
        if response['response'] == 100:
            self.access_token = response['data']['access_token']
            time.sleep(0.1)
            return self.getAuthUrl()
        else:
            return self.notify.send({
                "账号": self.getName(),
                "状态": "登录失败！"
            })

    def getAuthUrl(self):
        url = "https://f.yiban.cn/iapp/index"
        param = {
            "act":"iapp7463"
        }
        header = {
            "authorization": f"Bearer {self.access_token}",
            "logintoken": self.access_token
        }
        self.sess.get(f"https://f.yiban.cn/iapp7463",headers=header,allow_redirects=False)
        time.sleep(0.1)
        response = self.sess.get(url=url,params=param,headers=header,allow_redirects=False)
        self.verify = response.headers['Location']
        self.verify_request = re.findall(r"verify_request=(.*?)&", self.verify)[0]
        time.sleep(0.1)
        return self.auth()

    def auth(self):
        url = "https://api.uyiban.com/base/c/auth/yiban"
        self.sess.headers.update({
            'origin': 'https://app.uyiban.com',
            'referer': 'https://app.uyiban.com/',
            'Host': 'api.uyiban.com',
            'user-agent': 'yiban'
        })
        param={
            "verifyRequest":self.verify_request,
            "CSRF":self.csrf
        }
        self.sess.get(url=url,params=param)
        time.sleep(0.1)
        return self.CompletedList()

    def CompletedList(self):
        yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        url = f"https://api.uyiban.com/officeTask/client/index/completedList?StartTime={yesterday}%2000%3A00&EndTime={today}%2023%3A59&CSRF={self.csrf}"
        response = self.sess.get(url=url).json()
        if response['code'] == 0:
            if len(response['data']) > 0:
                for sub in response['data']:
                    if sub['Title'] == f"学生每日健康打卡({time.strftime('%Y-%m-%d', time.localtime())}）":
                        return self.notify.send({
                            "账号": self.getName(),
                            "状态" :"今日已打卡"
                        },isNotify=True)
                else:
                    dic = [content for content in response['data'] if re.findall(f"学生每日健康打卡\({time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))}）",content['Title']) !=[]]
                    if len(dic) == 1:
                        self.CompletedTaskID  = dic[0]['TaskId']
                        time.sleep(0.1)
                        return self.getInitiateId()
                    else:
                        return self.notify.send({
                            "账号": self.getName(),
                            "事件": "昨日存在多个任务，尝试调用打卡记录",
                            "状态": "多任务筛选失败，故不进行打卡！"
                        })
            elif len(response['data']) ==0:
                return self.notify.send({
                    "账号": self.getName(),
                    "状态": "昨日无任务，调用历史信息失败！"
                })
        elif response['code'] == 999:
            return self.notify.send({
                "账号": self.getName(),
                "状态": "易知独秀未被授权,请手动登录手机易班授权易知独秀！"
            })

    def getInitiateId(self):
        url = f"https://api.uyiban.com/officeTask/client/index/detail"
        param = {
            "TaskId":self.CompletedTaskID,
            "CSRF": self.csrf
        }
        response = self.sess.get(url=url,params=param).json()
        self.InitiateId = response['data']['InitiateId']
        time.sleep(0.1)
        return self.getClockInMess()

    def getClockInMess(self):
        url = f"https://api.uyiban.com/workFlow/c/work/show/view/{self.InitiateId}"

        param = {
            "CSRF": self.csrf
        }
        self.result = self.sess.get(url=url,params=param).json()
        time.sleep(0.1)
        return self.unCompletedList()

    def unCompletedList(self):
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        url = f"https://api.uyiban.com/officeTask/client/index/uncompletedList?StartTime={today}%2000%3A00&EndTime={today}%2023%3A59&CSRF={self.csrf}"
        response = self.sess.get(url=url).json()
        if response['code'] == 0:
            if len(response['data']) == 1:
                self.unCompletedTaskID = response['data'][0]['TaskId']
                time.sleep(0.1)
                return self.getWFId()
            elif len(response['data']) == 0:
                return self.notify.send({
                    "账号": self.getName(),
                    "状态": "任务未发布，故不继续执行！"
                })
            elif len(response['data']) > 1:
                dic = [content for content in response['data'] if re.findall(f"学生每日健康打卡\({time.strftime('%Y-%m-%d', time.localtime(time.time()))}）",content['Title']) !=[]]
                if len(dic) == 1:
                    self.unCompletedTaskID  = dic[0]['TaskId']
                    time.sleep(0.1)
                    return self.getWFId()
                else:
                    return self.notify.send({
                        "账号": self.getName(),
                        "事件": "存在多个任务，尝试进行筛选",
                        "状态": "筛选失败，故不进行打卡！"
                    })
        else:
            return self.notify.send({
                "账号": self.getName(),
                "事件": response['message'],
                "状态": "请手动检查易班是否正常！"
            })

    def getWFId(self):
        url = f"https://api.uyiban.com/officeTask/client/index/detail"
        param = {
            "TaskId":self.unCompletedTaskID,
            "CSRF": self.csrf
        }
        response = self.sess.get(url=url,params=param).json()
        if round(time.time()) > response['data']['StartTime']:
            self.WFId = response['data']['WFId']
            self.title = response['data']['Title']
            time.sleep(0.1)
            return self.isUpdate()
        else:
            return self.notify.send({
                "账号": self.getName(),
                "状态": "未到打卡时间！"
            })

    def isUpdate(self):
        url = f"https://api.uyiban.com/workFlow/c/my/form/{self.WFId}"
        param = {
            "CSRF":self.csrf
        }
        response = self.sess.get(url=url,params=param).json()
        if response['data']['Id'] == self.result['data']['Initiate']['WFId']:
            time.sleep(0.1)
            return self.clockIn()
        else:
            return self.notify.send({
                "账号": self.getName(),
                "事件":"打卡内容已更新，请手动打卡！",
                "状态": "打卡失败！"
            })

    def clockIn(self):
        url = f"https://api.uyiban.com/workFlow/c/my/apply/{self.WFId}"
        param = {
            "CSRF":self.csrf
        }
        data= {
            'data' :json.dumps({
                "a441d48886b2e011abb5685ea3ea4999":
                    {
                        "time":time.strftime('%Y-%m-%d %H:%M',time.localtime()),
                        "longitude":self.result['data']['Initiate']['FormDataJson'][0]['value']['longitude'],
                        "latitude":self.result['data']['Initiate']['FormDataJson'][0]['value']['latitude'],
                        "address":self.result['data']['Initiate']['FormDataJson'][0]['value']['address']
                    },
                "9cd65a003f4a2c30a4d949cad83eda0d":self.result['data']['Initiate']['FormDataJson'][1]['value'],
                "65ff68aeda65f345fef50b8b314184a7":self.result['data']['Initiate']['FormDataJson'][2]['value'],
                "b36100fc06308abbd5f50127d661f41e":self.result['data']['Initiate']['FormDataJson'][3]['value'],
                "c693ed0f20e629ab321514111f3ac2cb":self.result['data']['Initiate']['FormDataJson'][4]['value'],
                "91b48acca5f53c3221b01e5a1cf84f2f":self.result['data']['Initiate']['FormDataJson'][5]['value'],
                "9c96c042296de3e31a2821433cfec228":self.result['data']['Initiate']['FormDataJson'][6]['value'],
                "fd5e5be7f41a011f01336afc625d2fd4":self.result['data']['Initiate']['FormDataJson'][7]['value'],
                "c4b48d92f1a086996b0b2dd5f853c9f7":self.result['data']['Initiate']['FormDataJson'][8]['value']
            },ensure_ascii=False),
            "extend":json.dumps(
                {
                    "TaskId":self.unCompletedTaskID,
                    "title":self.result['data']['Initiate']['ExtendDataJson']['title'],
                    "content":[
                        {"label":self.result['data']['Initiate']['ExtendDataJson']['content'][0]['label'],"value":self.title},
                        {"label":self.result['data']['Initiate']['ExtendDataJson']['content'][1]['label'],"value":self.result['data']['Initiate']['ExtendDataJson']['content'][1]['value']}]
                },ensure_ascii=False)
        }
        response = self.sess.post(url=url,params=param,data=data).json()
        if response['code'] == 0:
            return self.notify.send({
                "账号": self.getName(),
                "状态": "打卡成功!"
            })
        else:
            return self.notify.send({
                "账号": self.getName(),
                "状态": "打卡失败！",
                "原因": response['msg']
            })

def main(admin,accounts):
    for each in accounts:
        if each['account'] != "" and each['password'] != "":
            yiBan = YiBan(admin,each)
            for count in range(3):
                try:
                    time.sleep(random.randint(2,5))    # 随机延时
                    yiBan.login()
                    break
                except requests.exceptions.ConnectionError:
                    print(f"{yiBan.getName()}\t请求失败，随机延迟后再次访问")
                    time.sleep(random.randint(2,5))
                    continue
            else:
                yiBan.notify.send({
                    "账号": yiBan.getName(),
                    "状态": "打卡失败！",
                    "原因": "多次请求失败，暂不打卡！"
                })
                break
    Notify.sendTotal(allMsg)

if __name__ == '__main__':
    main(admin,accounts)
