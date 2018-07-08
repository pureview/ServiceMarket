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
template_tixianchenggong="SyGbjc8pdi5ztIR7zgCfyaaxuY0jsp9Ou7n6ezOqyuw"
template_mission="bsgx4w4kMiQLIP91RFic-k5eMEyZPp0lKxZkMLj7l78"
template_upgrade="kjJIAqOOKcszyqGfzw1Y8kxlj1AQLUNGTqRUr49uSm8"
template_check_fail="vcbHE5Wgw-H8QY3vBREg36E3fOawJ2dhC2xB6_DC1gY"
template_commission="c_U0oGBgmyhernPk-8vUW7pajOMIwC0c74jyLOatG-Q"
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
                        "value":"现金红包已发放",
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
                       "value":"任务领取成功，点击进入继续任务",
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

def push_cando_mission(openid,current_time):  #通知某人可以进行下一次任务了
    js= {
           "touser":openid,
           "template_id":template_mission,
           "data":{
                   "first": {
                       "value":"经系统检测，您的账号满足做单条件，请您及时做单哦，么么哒",
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
                        "value":"请进入工作平台完成下一次任务",
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


if __name__=='__main__':
    #push_upgrade('ot0Np0wsM94zW5wa83HpEZhletIM')
    push_take_order('ot0Np0wsM94zW5wa83HpEZhletIM','13','今天','')
    #push_cash_success('ot0Np0wsM94zW5wa83HpEZhletIM','1','今天')
    #send_sms_code('17888835311','7980')
    #push_lingqurenwu('oWN6l065lkCa_LbJNlvksAarzYP0','aa','2018 6 11 16:33','www.qq.com')
