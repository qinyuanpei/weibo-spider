# -*- coding: utf-8 -*-  

import re
import sys
import rsa
import json
import base64
import binascii
import requests
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

class WeiboSpider:
    def __init__(self):
        self.session = requests.session()
        self.login_URL = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        self.loginPre_URL = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_='

    def loginPre(self):
        resp = self.session.get(self.loginPre_URL)
        html = re.findall(r'{.*}',resp.text)[0]
        data = json.loads(html)
        return data
    
    def login(self,username,password,data):
        servertime = data['servertime']
        nonce = data['nonce']
        pubkey = data['pubkey']
        rsakv = data['rsakv']

        su = base64.b64encode(username.encode(encoding='utf-8'))

        rsaPublicKey = int(pubkey,16)
        key = rsa.PublicKey(rsaPublicKey,65537)
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
        sp = binascii.b2a_hex(rsa.encrypt(message.encode(encoding='utf-8'),key))

        postdata = {
            'entry':'weibo',
            'gateway':'1',
            'from':'',
            'savestate':'7',
            'userticket':'1',
            'ssosimplelogin':'1',
            'vsnf':'1',
            'vsnal':'',
            'su':su,
            'service':'miniblog',
            'servertime':servertime,
            'nonce':nonce,
            'pwencode':'rsa2',
            'sp':sp,
            'encoding':'UTF-8',
            'url':'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype':'META',
            'rsakv':rsakv
        }

        resp = self.session.post(self.login_URL,data=postdata)
        print resp

    def fetch(self,uid):
        resp = self.session.get('http://weibo.cn/u/' + uid)
        html = resp.text.encode('gbk','ignore')
        soup = BeautifulSoup(resp.text,'html.parser',from_encoding='utf-8')
        total = soup.title
        print total
       
        

if(__name__ == "__main__"):
    spider = WeiboSpider()
    data = spider.loginPre()
    spider.login('qinyuanpei@sina.com','WEIBO85374216',data)
    spider.fetch('5566882921')

