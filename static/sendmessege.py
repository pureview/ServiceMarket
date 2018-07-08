import json
import requests
from collections import OrderedDict
import urllib.request
import urllib.parse


f = open('/home/ubuntu/taobao/static/asstoken.txt', 'r')
asstoken=f.read() #获取asstoken
f.close()
#注册成功通知
template_signin_success="6OP0dcdlTgE4Plg90DZdNuOYWfUqfQEK6cQ-H5CxHKY"
template_get_money="SyGbjc8pdi5ztIR7zgCfyaaxuY0jsp9Ou7n6ezOqyuw"
template_mission="bsgx4w4kMiQLIP91RFic-k5eMEyZPp0lKxZkMLj7l78"
template_upgrade="kjJIAqOOKcszyqGfzw1Y8kxlj1AQLUNGTqRUr49uSm8"
template_check_fail="vcbHE5Wgw-H8QY3vBREg36E3fOawJ2dhC2xB6_DC1gY"
template_commission="c_U0oGBgmyhernPk-8vUW7pajOMIwC0c74jyLOatG-Q"

apiurl="https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+asstoken

def push_sign_success(openid,usr_id,sign_time):           #注册成功接口
    
 
    js= {
           "touser":openid,
           "template_id":template_signin_success,
       
           
           "data":{
                   "first": {
                       "value":"注册成功,审核通过",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":usr_id,
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":sign_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"您现在可以使用本平台",
                        "color":"#173177"
                   }
                   
                   
           }
       }

    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)


def push_get_money(openid,money,tixian_time):   #三个参数，openid 用户名 和注册时间   提现通知接口
    js= {
           "touser":openid,
           "template_id":template_get_money,
       
           
           "data":{
                   "first": {
                       "value":"提现成功",
                       "color":"#173177"
                   },
                   "money":{
                       "value":money,
                       "color":"#173177"
                   },
                   "timet": {
                       "value":tixian_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"现金红包已发放",
                        "color":"#173177"
                   }
                   
                   
           }
       }    

    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)
    
def push_get_mission(openid,mission_id,mission_time,misson_url):  #参数分别为任务编号，时间，任务页面的url  
    js= {
           "touser":openid,
           "template_id":template_mission,
           "url":misson_url,
       
           
           "data":{
                   "first": {
                       "value":"任务领取成功",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":mission_id+"通过",
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":mission_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"点击详情，进入做任务界面",
                        "color":"#173177"
                   }
                   
                   
           }
       }    
    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)   

    
def push_cando_mission(openid,current_time):  #通知某人可以进行下一次任务了
    js= {
           "touser":openid,
           "template_id":template_mission,
           
       
           
           "data":{
                   "first": {
                       "value":"经系统检测，您绑定帐号满足做单条件",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":"允许下一次任务",
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":current_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"请您即时做单，么么哒",
                        "color":"#173177"
                   }
                   
                   
           }
       }    
    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)   
    
    
    
def push_upgrade(openid):    #徒弟升级为师傅通知
    
 
    js= ({
           "touser":openid,
           "template_id":template_upgrade,
       
           
           "data":{
                   "first": {
                       "value":"恭喜升级",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":"升级为师傅",
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":"通过",
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"恭喜升级",
                        "color":"#173177"
                   }
                   
                   
           }
       })

    
    
    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)   


def push_check_fail(openid,current_time):  #审核失败通知
    js= {
           "touser":openid,
           "template_id":template_check_fail,
           "data":{
                   "first": {
                       "value":"任务审核失败",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":"失败",
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":current_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"请联系售后客服",
                        "color":"#173177"
                   }
                   
                   
           }
       }    
    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)   

def push_getmoney_fromstudent(openid,money,current_time):   #三个参数 师傅收到徒弟每笔交易分成佣金的通知
    js= {
           "touser":openid,
           "template_id":template_commission,
       
           
           "data":{
                   "first": {
                       "value":"收到来自徒弟的交易分成",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":money,
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":current_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"这是来自徒弟分成的佣金",
                        "color":"#173177"
                   }
                   
                   
           }
       }    

    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text) 

def push_check_success(openid,current_time):  #任务审核成功，请前往后台提现
    js= {
           "touser":openid,
           "template_id":template_mission,
       
           
           "data":{
                   "first": {
                       "value":"任务审核成功",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":"通过",
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":current_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"请前往后台提现",
                        "color":"#173177"
                   }
                   
                   
           }
       }    
    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)       
    

    
if __name__ == '__main__':
    push_getmoney_fromstudent('ot0Np05y9oxcc6Yavz0-zrOxIgrg',100,'2018.7.2')
    push_check_fail('ot0Np05y9oxcc6Yavz0-zrOxIgrg','2019.2.2')
    push_check_success('ot0Np05y9oxcc6Yavz0-zrOxIgrg','2012.2.21')
    


 
