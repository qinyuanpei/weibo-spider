import nltk
import jieba
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

# def similarText(tokens,content):

# 创建特征
def buildFeatures(sentence,document):
    tokens = jieba.analyse.extract_tags(sentence)
    tokens = list(filter(lambda x:x.strip() not in stopwords, tokens))
    features = {}
    for (subject,contents) in document.items():
        for content in contents:
            snow = SnowNLP(tokens)
            f = open('log.txt','wt')
            text = ''
            for vector in snow.sim(content):
                text+=',' + str(vector)
                f.write('[' + text + ']\n')
            if(max(snow.sim(content))>0.99):
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

document = loadDocument(subjects)
connect = sqlite3.connect('data.db')
cursor = connect.cursor()
sql = "SELECT Post, Tags FROM table_weibo WHERE Tags <> ''"
cursor.execute(sql)
rows = cursor.fetchall()
features = [buildFeatures(row[0],document) for row in rows[0:100]]
length = len(features)
print('all features: ' + str(length))
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
    print("subject {0} is: {1}".format(key,freq))


