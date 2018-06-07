import pymysql

class DBHelper:
    def __init__(self,cursorType=None):
        if cursorType==None:
            self.db=pymysql.connect('localhost','root','z121212','taobao',charset='utf8mb4')
        else:
            self.db=pymysql.connect('localhost','root','z121212','taobao',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

    def query(self,statement):
        try:
            with self.db.cursor() as cursor:
                cursor.execute(statement)
                ret=cursor.fetchall()
                return ret 
        except Exception as e:
            print(statement)
            print(e)
            return None
        
    def commit(self,statement):
        try: 
            with self.db.cursor() as cursor:
                cursor.execute(statement)
                self.db.commit()
                return '0' 
        except Exception as e:
            print(statement)
            print(e)
            return '255'

