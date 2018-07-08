import requests

data=dict()
data['open_id']='oWN6I06odGU-NfKEm97hQhuMjuNk'
data['money']=1
requests.post('http://work-flow.cn:8964/pay_cash',data)
