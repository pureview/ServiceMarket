import time

import json
from collections import OrderedDict
import urllib.request
import urllib.parse

appid="wx1c61776edae08975"
appsecret="15625151323fe35cccd702c5cf987e83"
def flush_asstoken():
    apiurl="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="+appid+"&secret="+appsecret
    req= urllib.request.Request(apiurl)
    response= urllib.request.urlopen(req).read().decode('utf-8')
    dict=json.loads(response)
    print(dict['access_token'])
    xieru=dict['access_token']
    
    f = open('/home/ubuntu/taobao/static/asstoken.txt', 'w')
    f.write(xieru)
    f.close()
    return xieru
flush_asstoken()
    
    
    
    

    
    
