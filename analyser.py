import nltk
import jieba
import random
import sqlite3
from snownlp import SnowNLP

# 定义停用词
stopwords = open('stopwords.txt','rt',encoding='utf-8').readlines()

# 定义用户词典
userwords = open('userwords.txt','rt',encoding='utf-8').readlines()
for word in userwords:
    jieba.add_word(word)

# 加载语料库
def loadDocument(fileName):
    document = {}
    with open(fileName,'rt',encoding='utf-8') as file:
        for line in file.readlines():
            kv = line.split(':')
            subject = kv[0].strip()
            content = kv[1].strip()
            if(subject not in document.keys()):
                contents = []
                contents.append(content)
                document[subject] = contents
            else:
                document[subject].append(content)
    return document 

# 创建特征
def buildFeatures(sentence,document):
    tokens = jieba.cut(sentence)
    tokens = list(filter(lambda x:x.strip() not in stopwords, tokens))
    features = {}
    for (subject,contents) in document.items():
        for content in contents:
            snow = SnowNLP(tokens)
            if(max(snow.sim(content))>0.85):
                if(subject in features):
                    features[subject]+=1
                else:
                    features[subject]=1
    total = sum(features.values())
    for subject in features.keys():
        features[subject] = features[subject] / total

    # 特征归一化
    subjects = ['身高','性格','车房','年龄','地区','星座']
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

document = loadDocument('features.txt')
connect = sqlite3.connect('data.db')
cursor = connect.cursor()
sql = "SELECT Post, Tags FROM table_weibo WHERE Tags <> ''"
cursor.execute(sql)
rows = cursor.fetchall()
features = [buildFeatures(row[0],document) for row in rows]
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


