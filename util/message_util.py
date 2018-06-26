import json
import requests
from collections import OrderedDict
import urllib.request
import urllib.parse
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError


f = open('/home/ubuntu/taobao/static/asstoken.txt', 'r')
asstoken=f.read() #获取asstoken
f.close()
#注册成功通知
template_zhucechenggong="lk0cr1UMS2S8dbQhNVjJVS7-jmmwliY2QUcNX8Oes2Y"
template_tixianchenggong="-ZOSlwHWO51w9eoPnInTgWOSLXRzO44B7BkjVv5AexA"
template_mission="QkhdSqOamPzWqztL2SEbwWf2nK5mfet0mHEjQ5grpS4"

apiurl="https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+asstoken

def push_register_success(openid,usr_id,sign_time):
    js= ({
           "touser":openid,
           "template_id":template_zhucechenggong,
           "data":{
                   "first": {
                       "value":"conguratulation",
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
                        "value":"welcome",
                        "color":"#173177"
                   }
           }
       })
    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)

def push_cash_success(openid,money,tixian_time):   #三个参数，openid 用户名 和注册时间 
    js= {
           "touser":openid,
           "template_id":template_tixianchenggong,
           "data":{
                   "first": {
                       "value":"提现成功",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":money,
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":tixian_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"现金红包已发放，请点击\"服务通知\"，到聚分云领取红包",
                        "color":"#173177"
                   }
           }
       }    

    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)
    
def push_take_order(openid,mission_id,mission_time,misson_url):  #参数分别为任务编号，时间，任务页面的url
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
                       "value":mission_id,
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":mission_time,
                       "color":"#173177"
                   },
                   "remark": {
                        "value":"",
                        "color":"#173177"
                   }
           }
       }    
    response=requests.post(apiurl,data=json.dumps(js))
    print(response.text)      

def send_sms_code(phone,code):
    ####### Config #######
    appid=1400103992
    appkey='3538f89c3ae924b6fcbd2ec2242f7c7b'
    templateid=144636
    ######################
    phone=str(phone)
    code=str(code)
    ssender = SmsSingleSender(appid, appkey)
    params=[code,2]
    try:
        result = ssender.send_with_param(86, phone,
            templateid,params)
    except HTTPError as e:
        print(e)
        return 255
    except Exception as e:
        print(e)
        return 255
    print(result)
    return 0

if __name__=='__main__':
    send_sms_code('17888835311','7980')
    #push_lingqurenwu('oWN6l065lkCa_LbJNlvksAarzYP0','aa','2018 6 11 16:33','www.qq.com')
