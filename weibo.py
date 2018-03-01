# -*- coding: utf-8 -*-  
import re
import sys
import time
import json
import jieba
import sqlite3
import base64
import binascii
import requests
from bs4 import BeautifulSoup
from os import path
from PIL import Image
import numpy as np
import jieba
jieba.load_userdict("userdict.txt")
import jieba.posseg as pseg
from snownlp import SnowNLP
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
import timer

class WeiboSpider:
    def __init__(self):
        self.session = requests.session()
        self.connect = sqlite3.connect('data.db')
        self.cursor = self.connect.cursor()
        self.cookies = {'Cookie':'_T_WM=cb533a40185d08956a509dd3e160b837; SUB=_2A253frswDeRhGedM7FoX8CfOyD2IHXVUgMV4rDV6PUJbkdANLWX8kW1NWD4ssUZbwJYzHK16NYAxjjeDemzSaIya; SUHB=0FQqVzkhJmylMv; SCF=Aoo4SbjmA7AfDLSz2MMUYI2LYIbthnKpbwe20xACnbRMnUGHQuRaDo-qS5qDlWusErJ_M9OY3Ip6z7Tz-NP26J4.'}
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
            'Refer':'https://weibo.cn/'
        }
        self.initSqlite()

    def fetch(self,uid):
        html = self.request('http://weibo.cn/u/' + uid)
        soup = BeautifulSoup(html,'html.parser',from_encoding='utf-8')

        #count = self.matchPages(soup)
        count = 660
        for page in range(500,count+1):
            time.sleep(10)
            print(u'正在抓取页面：' + 'https://weibo.cn/u/' + uid + '?page=' + str(page))
            html = self.request('https://weibo.cn/u/' + uid + '?page=' + str(page))
            soup = BeautifulSoup(html,'html.parser',from_encoding='utf-8')
            print(u'正在写入页面：' + 'https://weibo.cn/u/' + uid + '?page=' + str(page))
            texts = self.matchMain(soup)
            for text in texts:  
                self.fillSqlite(text)

        self.cursor.execute('''SELECT Text FROM table_weibo''')
        rows = self.cursor.fetchall()
        print(u'共抓取微博数据' + str(len(rows)) + u'条')
        self.connect.commit()
    
    def matchMain(self,soup):
        divs = soup.find_all('div',id=re.compile('M_([\s\S]+?)|M_'))
        posts = []
        for div in divs:
            details = self.matchDetails(div)
            if(details != None):
                html = self.request(details)
                newSoup = BeautifulSoup(html,'html.parser',from_encoding='utf-8')
                results = self.matchMain(newSoup)
                if(len(results)>0):
                    posts.append(self.matchMain(newSoup)[0])
            else:
                posts.append(div.div.span.get_text().encode('utf-8'))
        return posts

    def matchPages(self,soup):
        pages = soup.find('div',attrs={'id':'pagelist'}).form.div.contents[-1].strip()
        pages = pages.split('/')[1]
        pages = int(re.findall(r'\d+', pages)[0])
        return pages

    def matchDetails(self,post):
        for child in post.div.span:
            if(child.string == None) or (child.name!='a'):
                continue
            if(child.name =='a') and (child.string.encode('gbk','ignore').decode('gbk') == u'全文'):
                return 'https://weibo.cn' + str(child['href'])
        return None
    
    def initSqlite(self):
        self.connect.text_factory= str
        sql = '''CREATE TABLE IF NOT EXISTS table_weibo
        (
            ID INTEGER PRIMARY KEY autoincrement,
            Text VARCHAR(500) NOT NULL,
            Wish VARCHAR(500)
        )'''

        self.cursor.execute(sql)
        print(u'数据库初始化完成!')

    def fillSqlite(self,value):
        sql = 'INSERT INTO table_weibo VALUES(NULL,?,?)'
        self.cursor.execute(sql,(value,''))
        self.connect.commit()

    def request(self,URL):
        resp = self.session.get(URL,cookies=self.cookies,headers=self.headers)
        html = resp.text.encode('gbk','ignore').decode('gbk')
        return html

    def analyse(self):
        # Adjust Data
        self.adjustData()

        # Split Words
        self.splitWords()
        
        # Generate Report
        self.generateReport()

    def splitWords(self):
        # Filter Data
        sql = "SELECT ID, Wish FROM table_weibo WHERE Wish <> ''"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        # Split Words
        sql = "UPDATE table_weibo SET Tags = ? WHERE ID = ?"
        for row in rows:
            id = row[0]
            wish = row[1]
            wish = wish.replace('\u3002','')
            wish = wish.replace('\uff0c','')
            wish = wish.replace('\u005b','')
            wish = wish.replace('\u005d','')
            wish = wish.replace('\u3010','')
            wish = wish.replace('\u3011','')
            tags = self.generateTags(wish)
            self.cursor.execute(sql,(tags,id))
        self.connect.commit()

    def generateTags(self,text):
        snow = SnowNLP(text)
        sentences = snow.tags
        tags = []
        for s in sentences:
            words = pseg.cut(s[0])
            for w in words:
                tags.append({'word':w.word,'flag':w.flag})
        return json.dumps(tags)

    def generateReport(self):
        # Filter Data
        sql = "SELECT Post, Tags FROM table_weibo WHERE Tags <> ''"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        # Filter Tags
        male_tags = ''
        female_tags = ''
        for row in rows:
            post = row[0]
            tags = json.loads(row[1])
            snow = SnowNLP(row[0])
            if u'男嘉宾[向右]' in post:
                female_tags += ','.join(map(lambda x:x['word'],tags))
            elif u'女嘉宾[向右]' in row[0]:
                male_tags += ','.join(map(lambda x:x['word'],tags))
                
        # WordCloud
        self.generateWordCloud(female_tags,'female.png','output_female.png')
        self.generateWordCloud(male_tags,'male.png','output_male.png')

    def adjustData(self):
        # Filter Data
        sql = "SELECT ID, Post FROM table_weibo WHERE POST LIKE '%%%%%s%%%%' OR POST LIKE '%%%%%s%%%%'"
        sql = sql % (u'#征婚交友#',U'#月老爱牵线#')
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        # Adjust Data
        patterns = ['想找','希望找','要求','希望另一半','择偶标准','希望对方',
        '希望','找一位','找一个','一半','找','想','喜欢','择偶条件','寻','期待','女孩',
        '男孩','女生','男生','女士','男士','理想型']
        sql = "UPDATE table_weibo SET Wish = ? WHERE ID = ?"
        for row in rows:
            id = row[0]
            post = row[1]
            match = -1
            for pattern in patterns:
                if(pattern in post):
                    match = post.find(pattern) + len(pattern)
                    break
            if(match != -1):
                wish = str(post[match:])
                wish = wish.replace('#西安月老牵线#','')
                wish = wish.replace('[心]@月老蜀黍' ,'')
                wish = wish.replace('#月老爱牵线#'  ,'')
                self.cursor.execute(sql,(wish,id))
            else:
                self.cursor.execute(sql,('',id))
        self.connect.commit()

    def generateWordCloud(self,text,background,output):
        back_coloring = np.array(Image.open(background))
        #stopwords = set(STOPWORDS)
        #stopwords.add(u'西安')
        #stopwords.add(u'生活')
        wordcloud = WordCloud(
            font_path='simfang.ttf',  # 设置字体
            background_color="white",  # 背景颜色
            max_words=5000,  # 词云显示的最大词数
            mask=back_coloring,  # 设置背景图片
            stopwords=stopwords, #停用词设置
            max_font_size=75,  # 字体最大值
            random_state=42,
            width=1000, height=860, margin=15,# 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
        )

        wordcloud.generate(text)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()
        wordcloud.to_file(output)
    

if(__name__ == "__main__"):
    spider = WeiboSpider()
    spider.fetch('5566882921')
    spider.analyse()

