from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 绘制柱形图
def bar(title, data, xlabel, ylabel, fileName):
    labels = data.keys()
    values = data.values()
    plt.rcParams['font.sans-serif'] = ['simHei'] 
    plt.rcParams['axes.unicode_minus'] = False
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(range(len(labels)),labels)
    plt.legend(loc='upper right',)
    plt.bar(range(len(labels)), values, color = 'rgb')
    plt.title(title)
    plt.show()

# 绘制饼图
def pie(title, data, fileName):
    labels = data.keys()
    counts = data.values()
    colors = ['red','yellowgreen','lightskyblue']
    plt.figure(figsize=(8,5), dpi=80)
    plt.axes(aspect=1) 
    plt.pie(counts, #性别统计结果
            labels=labels, #性别展示标签
            colors=colors, #饼图区域配色
            labeldistance = 1.1, #标签距离圆点距离
            autopct = '%3.1f%%', #饼图区域文本格式
            shadow = False, #饼图是否显示阴影
            startangle = 90, #饼图起始角度
            pctdistance = 0.6 #饼图区域文本距离圆点距离
    )
    plt.legend(loc='upper right',)
    plt.title(title)
    plt.show()

# 绘制词云
def wordcloud(text,background,fileName):
    pass
