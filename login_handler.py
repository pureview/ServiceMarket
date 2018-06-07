import tornado.ioloop
import tornado.web
import json
from util.db import *

class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        ret=dict()
        ret['code']=255
        username=self.get_argument('username')
        passwd=self.get_argument('passwd')
        helper=DBHelper()
        statement='select passwd from seller where username="%s"'%(username)
        res=helper.query(statement)
        if len(res)>0:
            if passwd=res[0][0]:
                ret['code']=0
        self.write(json.dumps(ret,ensure_ascii=False))
