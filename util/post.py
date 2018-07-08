import requests

data={}
'''
data['wechat_id']='ot0Np0wsM94zW5wa83HpEZhletIM'
data['code']=39
data['seller_username']='test'
'''
data['code']=9
data['wechat_id']='oWN6I06odGU-NfKEm97hQhuMjuNk'
data['seller_username']='test'
data['user_order_id']=26041
data['order_id']=11111
#data='code=9&wechat_id=oWN6I06odGU-NfKEm97hQhuMjuNk&seller_username=test&user_order_id=26041&order_id=11111'
url='http://work-flow.cn:8080/mission'
print(requests.post(url,data).text)
