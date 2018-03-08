import nltk
import jieba
import random
import sqlite3
from snownlp import SnowNLP

stopwords = open('stopwords.txt','rt',encoding='utf-8').readlines()
userwords = open('userwords.txt','rt',encoding='utf-8').readlines()
for word in userwords:
    jieba.add_word(word)

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

def genderFeatures(sentence,document):
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

    subjects = ['身高','性格','车房','年龄','地区','星座']
    for subject in subjects:
        if(subject not in features.keys()):
            features[subject] = 0
    return features

document = loadDocument('features.txt')
connect = sqlite3.connect('data.db')
cursor = connect.cursor()
sql = "SELECT Post, Tags FROM table_weibo WHERE Tags <> ''"
cursor.execute(sql)
rows = cursor.fetchall()
features = features = [genderFeatures(row[0],document) for row in rows]
print(features)
# train_set = set(map(lambda x:(x[1],x[0]), features.items()))
# test_set = set(map(lambda x:(x[1],x[0]), features.items()))
# classifier = nltk.NaiveBayesClassifier.train(train_set)
# print(nltk.classify.accuracy(classifier,train_set))
# print(features)
