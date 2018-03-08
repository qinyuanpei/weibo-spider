class dbHelper(object):

    def __init__(self,dbName):
        self.dbName = dbName
        self.connect = sqlite3.connect(self.dbName)
        self.cursor = self.connect.cursor()
    
    def init_db(self):
        self.connect.text_factory= str
        sql = '''CREATE TABLE IF NOT EXISTS table_weibo
        (
            ID INTEGER PRIMARY KEY autoincrement,
            Text VARCHAR(500) NOT NULL,
            Wish VARCHAR(500),
            Tags VARCHAR(500)
        )'''
        self.cursor.execute(sql)
        print(u'数据库初始化完成!')

    def exec_sql(self,sql,values):
        pass
