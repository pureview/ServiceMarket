import tornado.ioloop
import tornado.web
import json
from redpack import *

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")
    def post(self):
        open_id=self.get_argument('open_id')
        money=int(self.get_argument('money'))
        ret=send_red_pack(open_id,money) 
        if ret['result_code']=='SUCCESS':
            ret['code']=0
        else:
            ret['code']=255
        ret['message']=ret['return_msg']
        self.write(json.dumps(ret,ensure_ascii=False))

def make_app():
    return tornado.web.Application([
        (r"/pay_cash", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8964)
    tornado.ioloop.IOLoop.current().start()
