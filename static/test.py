import tornado.ioloop
import tornado.web
import json
import os
import random
import time
import datetime
import logging
from collections import OrderedDict
import urllib.request
import urllib.parse    
    
    
def get_open_id(code,appid='wx61e83ce648e7b691',secret='9cbcf612af5c8a37d9840c060afd5ab8'):
    apiurl="https://api.weixin.qq.com/sns/oauth2/access_token?appid="+appid+"&secret="+secret+"&code="+code+"&grant_type=authorization_code"
    response= urllib.request.urlopen(apiurl).read().decode('utf-8')
    dict=json.loads(response)
    print(dict)
    for key in dict:
        if key == 'openid':
               # print (dict['openid'])
            return dict['openid']
                
                
                
fff= get_open_id('071lXjAE0g5hQc2IVMxE0Sr7AE0lXjAk')
print(fff)
