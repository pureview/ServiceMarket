# -*- coding: UTF-8 -*-

from hashlib import sha1
from time import time
from wx_pay import WxPay, WxPayError

api_cert_path = "/home/ubuntu/pem/apiclient_cert.pem"
api_key_path = "/home/ubuntu/pem/apiclient_key.pem"
      
def send_red_pack(openid,amount):
    """
    向个人用户发红包example
    """
    data={'send_name':u'禾梓先生',
      're_openid':openid,
      'total_amount':amount,
      'wishing':u'感谢使用本平台',
      'client_ip':u'139.199.96.148',
      'act_name':u'提现',
      'remark':u'请12小时内领取红包'}
    wx_pay = WxPay(
        wx_app_id='wx61e83ce648e7b691',
        wx_mch_id='1507994731',
        wx_mch_key='b8uww0npq5b53m1bqfv6c4wi8kln4giv',
        wx_notify_url='http://www.example.com/pay/weixin/notify'
    )
    '''
    raw = wx_pay.send_red_pack(
        # 证书获取方法请阅读：https://pay.weixin.qq.com/wiki/doc/api/tools/cash_coupon.php?chapter=4_3
        # api_cert_path: 微信支付商户证书（apiclient_cert.pem）的本地保存路径
        api_cert_path='/home/ubuntu/pem/apiclient_cert.pem',
        # api_cert_path: 微信支付商户证书（apiclient_key.pem）的本地保存路径
        api_key_path='/home/ubuntu/pem/apiclient_key.pem',
        send_name=u'红包测试',  # 红包名称
        re_openid=u'ot0Np01VZKOO3fz6ki6BA0VPCupc',  # 要接收红包的用户openid
        total_amount=100,  # total_fee 单位是 分， 100 = 1元, 最大499元
        wishing=u'***感谢参与测试***',  # 祝福语
        client_ip=u'139.199.96.148',  # 调用微信发红包接口服务器公网IP地址
        act_name=u'***微信支付测试系统***',  # 活动名称
        remark=u'***感谢参与***'  # 备注
    )
    '''
    raw = wx_pay.send_red_pack(api_cert_path,api_key_path,**data)
    print (WxPay.to_utf8(raw)) 
   
if __name__ == '__main__':
    print(requets.post('http://work-flow.cn:8964/pay_cash',{'open_id':'ot0Np0wsM94zW5wa83HpEZhletIM',money:100}).text)
    #send_red_pack('ot0Np05y9oxcc6Yavz0-zrOxIgrg',100)
    #send_red_pack('oWN6I06odGU-NfKEm97hQhuMjuNk',100)
