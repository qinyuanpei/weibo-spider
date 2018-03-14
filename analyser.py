import re
import math
import nltk
import jieba
import datetime
from jieba import analyse
import random
import sqlite3
from snownlp import SnowNLP
from collections import Counter

# 定义停用词
stopwords = open('stopwords.txt','rt',encoding='utf-8').readlines()

# 定义用户词典
userwords = open('userwords.txt','rt',encoding='utf-8').readlines()
for word in userwords:
    jieba.add_word(word)

# 定义文本主题
subjects = ['身高','性格','房车','年龄','地区','星座']

# 加载数据
def loadData():
    connect = sqlite3.connect('data.db')
    cursor = connect.cursor()
    sql = "SELECT Post, Tags FROM table_weibo WHERE Tags <> ''"
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

# 加载语料库
def loadDocument(subjects):
    document = {}
    for subject in subjects:
        fileName = './train_data/{0}.txt'.format(subject)
        with open(fileName,'rt',encoding='utf-8') as file:
            contents = file.readlines()
            if(subject not in document.keys()):
                document[subject] = contents
            else:
                document[subject].extend(content)
    return document 

# 文本相似度
def similarText(tokens,content):
    snow = SnowNLP(tokens)
    similar = snow.sim(content)
    norm = math.sqrt(sum(map(lambda x:x*x,similar)))
    if(norm == 0):
        return False
    similar = map(lambda x:x/norm,similar)
    return max(similar)>=0.95

# 创建特征
def buildFeatures(sentence,document):
    tokens = jieba.analyse.extract_tags(sentence)
    tokens = list(filter(lambda x:x.strip() not in stopwords, tokens))
    features = {}
    for (subject,contents) in document.items():
        for content in contents:
            if(similarText(tokens,content)):
                if(subject in features):
                    features[subject]+=1
                else:
                    features[subject]=1
    total = sum(features.values())
    for subject in features.keys():
        features[subject] = features[subject] / total

    # 特征归一化
    for subject in subjects:
        if(subject not in features.keys()):
            features[subject] = 0

    # 预测结果
    max_value = max(features.values())
    suggest_subject = ' '
    for (key,value) in features.items():
        if(value == max_value):
            suggest_subject = key
    return features, suggest_subject

# 年龄分布
def analyseAge(): 
    ages = []
    rows = loadData()
    pattern = re.compile(r'\d{2}\年|\d{2}\岁')
    for row in rows:
        text = row[0].decode('utf-8')
        matches = pattern.findall(text)
        if(len(matches)>0):
            match = matches[0]
            if(u'年' in match):
                now = datetime.datetime.now().year
                birth = int(''.join(re.findall(r'\d',match)))
                ages.append(now - 1900 - birth)
            else:
                ages.append(int(''.join(re.findall(r'\d',match))))
    
    print(ages)

# 性别组成
def analyseSex():
    rows = loadData()
    sexs = {'male':0, "female":0}
    for row in rows:
        text = row[0].decode('utf-8')
        if u'男嘉宾[向右]' in text:
            sexs['male']+=1
        elif u'女嘉宾[向右]' in text:
            sexs['female']+=1
    print('male:' + str(sexs['male']))
    print('female:' + str(sexs['female']))

# 身高分布
def analyseHeight():
    heights = []
    rows = loadData()
    pattern = re.compile(r'1\d{2}|\d{1}\.\d{1,2}|\d{1}\米\d{2}')
    for row in rows:
        text = row[0].decode('utf-8')
        matches = pattern.findall(text)
        if(len(matches)>1):
            matches = map(lambda x:int(''.join(re.findall(r'\d',x))),matches)
            matches = list(filter(lambda x: x<190 and x>150, matches))
            if(len(matches)>1):
                height = {} 
                height['male'] = max(matches)
                height['female'] = min(matches)
                heights.append(height)

# 房车分析
def analyseHouse():
    pass

# 地区分析
def anslyseLocation():
    freqs = { }
    citys = [u'西安',u'铜川',u'宝鸡',u'咸阳',u'渭南',u'延安',u'汉中',u'榆林',u'安康',u'商洛']
    rows = loadData()
    for row in rows:
        text = row[0].decode('utf-8')
        for city in citys:
            if(city in text):
                if(city in freqs.keys()):
                    freqs[city]+=1
                else:
                    freqs[city]=1
    print(freqs)
                       
# 星座分析
def analyseStar():
    pass

# 特征分析
def analyseFeatures():
    rows = loadData()
    document = loadDocument(subjects)
    features = [buildFeatures(row[0],document) for row in rows]
    length = len(features)
    print('total features: ' + str(length))
    cut_length = int(length * 0.5)
    print('train features: ' + str(cut_length))
    train_set = features[0:cut_length]
    print('test features: ' + str(length - cut_length + 1))
    test_set = features[cut_length:]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    train_accuracy = nltk.classify.accuracy(classifier,train_set)
    print('accuracy: ' + str(train_accuracy))

    counts = Counter(map(lambda x: x[1],test_set))
    for key, count in counts.items():
        freq = count/len(test_set)
        print("subject <{0}> is: {1}".format(key,freq))

# 词云分析
def anslyseWordcloud():
    pass

if(__name__ == '__main__'):
    analyseAge()
    analyseSex()
    analyseHeight()
    anslyseLocation()
    analyseFeatures()

    

