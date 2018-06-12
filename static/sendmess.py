#coding=utf8

import httplib
import json


f = open('/home/ubuntu/taobao/static/asstoken.txt', 'r')
asstoken=f.read() 
f.close()

template_zhucechenggong="lk0cr1UMS2S8dbQhNVjJVS7-jmmwliY2QUcNX8Oes2Y"
template_tixianchenggong="-ZOSlwHWO51w9eoPnInTgWOSLXRzO44B7BkjVv5AexA"
template_mission="QkhdSqOamPzWqztL2SEbwWf2nK5mfet0mHEjQ5grpS4"

#apiurl="https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+asstoken
#注册成功通知
def push_zhucechegngong(openid,usr_id,sign_time):   #三个参数，openid 用户名 和注册时间 
    js= {
           "touser":openid,
           "template_id":template_zhucechenggong,
       
           
           "data":{
                   "first": {
                       "value":"注册成功",
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
                        "value":"欢迎加入本平台",
                        "color":"#173177"
                   }
                   
                   
           }
       }    
    conn = httplib.HTTPConnection("api.weixin.qq.com:80")
    headers = {"Content-type":"application/json"} #application/x-www-form-urlencoded
    
    conn.request("POST", "/cgi-bin/message/template/send?access_token="+asstoken, json.JSONEncoder().encode(js), headers)
    response = conn.getresponse()
    data = response.read()
    if response.status == 200:
        print 'success'
        print data
    else:
        print 'fail'
    conn.close()
    
def push_tixianchenggong(openid,money,tixian_time):   #三个参数，openid 用户名 和注册时间 
    js= {
           "touser":openid,
           "template_id":template_tixianchenggong,
       
           
           "data":{
                   "first": {
                       "value":"提现成功成功",
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
    conn = httplib.HTTPConnection("api.weixin.qq.com:80")
    headers = {"Content-type":"application/json"} #application/x-www-form-urlencoded
    
    conn.request("POST", "/cgi-bin/message/template/send?access_token="+asstoken, json.JSONEncoder().encode(js), headers)
    response = conn.getresponse()
    data = response.read()
    if response.status == 200:
        print 'success'
        print data
    else:
        print 'fail'
    conn.close()

    
def push_lingqurenwu(openid,mission_id,mission_time,misson_url):
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
                        "value":"点击此消息，进入做任务界面",
                        "color":"#173177"
                   }
                   
                   
           }
       }    
    conn = httplib.HTTPConnection("api.weixin.qq.com:80")
    headers = {"Content-type":"application/json"} #application/x-www-form-urlencoded
    
    conn.request("POST", "/cgi-bin/message/template/send?access_token="+asstoken, json.JSONEncoder().encode(js), headers)
    response = conn.getresponse()
    data = response.read()
    if response.status == 200:
        print 'success'
        print data
    else:
        print 'fail'
    conn.close()
    
push_lingqurenwu('oWN6l0-ul013P5k5dQkcAUBlR6j8','123345456','2018 6 11 16:33','www.qq.com')
