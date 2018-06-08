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
from util.db import *
from util.logger import *

logger=get_logger()
myappkey="43b6ccf1-ec3d-4de9-98ca-156aa618a0e3"
apiurl=  "https://www.jufenyun.com/openapi/gateway"
class MissionHandler(tornado.web.RequestHandler):
    def secure_gate(self):
        # Check user identity whether username and wechat_id match.
        pass

    def get_wechat_id(self,code=None):
        '''
        获取微信openID
        '''
        if code==None:
            code=self.get_argument('wechat_code')
        return self.get_open_id(code)
    
    def get_username(self,wechat_id=None):
        '''
        根据微信openID获取用户名
        '''
        if wechat_id==None:
            wechat_id=self.get_username('wechat_id')
        helper=DBHelper()
        statement='select id from user where wechat_id="%s"'%(wechat_id)
        return helper.query(statement)[0][0]

    def post(self):
        '''
        url: /mission
        '''
        ###### Config ######
        num_per_page=10
        user_mission_interval=60*3 # 任务倒计时时间
        shop_interval_days=3 
        ####################
        ret=dict()
        ret['code']=255
        code=self.get_argument('code')
        seller_username=self.get_argument('seller_username','test_seller')
        helper=DBHelper()
        if code=='0':
            # 插入新的任务类别
            if seller_username=='':
                self.write(json.dumps(ret));return
            keyword=self.get_argument('keyword')
            sort=self.get_argument('sort')
            shop=self.get_argument('shop')
            if 'images' in self.request.files:
                file_metas=self.request.files['images']
                for meta in file_metas:
                    filename=meta['filename'].replace(' ','')
                    # Build file path
                    prefix='image/'+seller_username+'/'
                    if not os.path.exists(prefix):
                        os.mkdir(prefix)
                    new_file_name=prefix+filename
                    if os.path.exists(new_file_name):
                        filename=str(random.randint(0,10000))+filename
                        new_file_name=prefix+filename
                    with open(new_file_name,'wb') as up:
                        up.write(meta['body'])
                    task_image=new_file_name
            else:
                self.write(json.dumps(ret));return
            status='0'
            price=self.get_argument('price')
            pay_method=self.get_argument('pay_method')
            good_name=self.get_argument('good_name')
            good_price=self.get_argument('good_price')
            statement='insert into mission_class (seller_username,keyword,sort,task_image,status,price,'+\
                    'pay_method,good_name,good_price,create_date,shop)'+\
                    'values("%s","%s","%s","%s","%s","%s","%s","%s","%s",now(),"%s")'\
                    %(seller_username,keyword,sort,task_image,status,price,pay_method,good_name,good_price,shop)
            res=helper.commit(statement)
            ret['code']=res
        elif code=='1':
            # 插入新的任务数据
            mission_class=self.get_argument('mission_class')
            status=self.get_argument('status',"0")
            begin_time=self.get_argument('begin_time').replace('-','')
            end_time=self.get_argument('end_time').replace('-','')
            b_year,b_month,b_day,b_hour,b_minutes=int(begin_time[:4]),int(begin_time[4:6]),\
                int(begin_time[6:8]),int(begin_time[8:10]),int(begin_time[10:12])
            e_year,e_month,e_day,e_hour,e_minutes=int(end_time[:4]),int(end_time[4:6]),\
                int(end_time[6:8]),int(end_time[8:10]),int(end_time[10:12])
            begin_stamp=datetime.datetime(b_year,b_month,b_day,b_hour,b_minutes).timestamp()
            end_stamp=datetime.datetime(e_year,e_month,e_day,e_hour,e_minutes).timestamp()
            master_money=self.get_argument('master_money')
            slave_money=self.get_argument('slave_money')
            allow=self.get_argument('allow')
            # 查询任务类别 
            statement='select shop from mission_class where id="%s"'%(mission_class)
            shop=helper.query(statement)[0][0]
            statement='insert into mission_object (mission_class,status,begin_time,end_time,master_money,slave_money,allow,create_date,seller_username,shop)'+\
                    'values ("%s","%s","%s","%s","%s","%s","%s",now(),"%s","%s")'\
                    %(mission_class,status,str(begin_stamp),str(end_stamp),master_money,slave_money,allow,seller_username,shop)
            res=helper.commit(statement)
            # 更新任务类别状态
            statement='update mission_class set status="1" where id="%s"'%(mission_class)
            res=helper.commit(statement)
            ret['code']=res
        elif code=='2':
            '''
            获取任务类别列表
            op操作码：0代表查询页数，1代表获取特定页数的信息
            '''
            helper=DBHelper(1)
            op=int(self.get_argument('op',1))
            if op==0:
                statement='select count(*) from mission_class where seller_username="%s"'%(seller_username)
                ret['count']=helper.query(statement)
                ret['page_num']=num_per_page
            elif op==1:
                page=int(self.get_argument('page',-1))
                statement='select count(*) from mission_class where seller_username="%s"'%(seller_username)
                ret['count']=helper.query(statement)
                ret['page_num']=num_per_page
                ret['code']=0 
                if page==-1:
                    # 选择所有数据，将分段加载交给前端
                    statement='select id,seller_username,keyword,sort,task_image,status,price,pay_method,good_name,'+\
                        'good_price,shop from mission_class where seller_username="%s" order by create_date desc '\
                        %(seller_username)
                else:
                    statement='select id,seller_username,keyword,sort,task_image,status,price,pay_method,good_name,'+\
                        'good_price,shop from mission_class where seller_username="%s" order by create_date desc limit %d,%d'\
                        %(seller_username,page*num_per_page,num_per_page)
                #print(statement)
                res=helper.query(statement)
                # 更新任务状态
                now=time.time()
                for mission in res:
                    if mission['status']==1 and float(mission['end_time'])<now:
                        statement='update mission_class set status="0" where id="%d"'%(mission['id'])
                        helper.commit(statement)
                        mission['status']=0
                ret['data']=res
            else:
                pass
        elif code=='3':
            # @hidden: 在前端暂时不可见
            # 获取发布任务列表
            helper=DBHelper(1)
            ret['code']=0 
            page=int(self.get_argument('page',-1))
            if page==-1:
                # 选择所有数据，将分段加载交给前端
                statement='select id,mission_class,status,begin_time,end_time,master_money,slave_money,allow,shop '+\
                    'from mission_object where seller_username="%s" order by create_date desc'\
                    %(seller_username)
            else:
                statement='select id,mission_class,status,begin_time,end_time,master_money,slave_money,allow,shop '+\
                    'from mission_object where seller_username="%s" order by create_date desc limit %d,%d'\
                    %(seller_username,page*num_per_page,num_per_page)
            res=helper.query(statement)
            ret['data']=res
        elif code=='4':
            # @deprecated
            # 获取任务类别分页数
            statement='select count(*) from mission_class where seller_username="%s"'%(seller_username)
            res=helper.query(statement)
            ret['code']=0 
            ret['data']=int(res)/num_per_page
        elif code=='5':
            # @deprecated
            # 获取任务分页数
            statement='select count(*) from mission_object where seller_username="%s"'%(seller_username)
            res=helper.query(statement)
            ret['code']=0 
            ret['data']=int(res)/num_per_page
        elif code=='6':
            # 删除任务类别
            mission_id=self.get_argument('id')
            statement='delete from mission_class where id="%s" and where seller_username="%s"'%(mission_id,seller_username)
            ret['code']=helper.commit(statement)
        elif code=='7':
            # 取消任务
            mission_class=self.get_argument('id')
            # 查询已经激活的mission_object
            statement='select id where mission_class="%s" and status="0"'%(mission_class)
            res=helper.query(statement)
            if res==None or len(res)==0:
                ret['message']='没有正在执行的任务'
                self.write(json.dumps(ret));return
            mission_object=res[0][0]
            statement='update mission_object set status="1" where id="%s"'%(mission_object)
            helper.commit(statement)
            # 更改任务类别状态
            statement='update mission_class set status="1" where id="%s"'%(mission_class)
            ret['code']=helper.commit(statement)
        elif code=='8':
            '''
            申请任务
            业务逻辑：查询当前可用任务，如果可用，更新状态，返回一个订单，否则返回没有订单
            ''' 
            self.secure_gate()
            username=self.get_username()
            wechat_id=self.get_argument('wechat_id')
            ret['data']=dict()
            # Query user's identity
            statement='select role,black_list,mission_interval from user where wechat_id="%s"'%(username)
            res=helper.query(statement)
            if len(res)>0:
                role,black_list=res[0]
                if (black_list!=None and black_list!=0) or role==None or role==0:
                    self.write(json.dumps(ret));return
            else:
                self.write(json.dumps(ret));return
            user_interval=res[0][2]
            # Select user mission record
            statement='select id,mission_id,accept_time,finish_time,shop '+\
                    'from user_order where seller_username="%s" and username="%s" and status<"3" order by '+\
                    'accept_time desc limit 100'
            res=helper.query(statement)
            shop_dict=self.get_shop_dict(res,user_interval)
            # Query active 
            statement='select id,mission_class,begin_time,end_time,master_money,slave_money,allow,last_timestamp'+\
                    ',mission_num,good_num,shop from mission_object '+\
                    'where seller_username="%s" and status="0"'
            res=helper.query(statement)
            for row in res:
                mission_id,mission_class,begin_time,end_time,master_money,slave_money,allow,last_timestamp,mission_num,good_num,shop=row
                if shop in shop_dict:
                    continue
                # Calculate time interval
                if allow==1 and role!=2:
                    self.write(json.dumps(ret));return
                if mission_num==0 or good_num==0:
                    self.write(json.dumps(ret));return
                interval=(float(end_time)-float(begin_time))/mission_num
                cur_timestamp=time.time()
                if last_timestamp==None:
                    pass
                else:
                    if cur_timestamp-float(last_timestamp)>interval:
                        pass
                    else:
                        self.write(json.dumps(ret));return
                # Write current timestamp 
                statement='update mission_object set last_timestamp="%s" where id="%s"'%(str(cur_timestamp),mission_id)
                res_=helper.commit(statement)
                if res_!=0:
                    self.write(json.dumps(ret));return
                # Successfully get mission
                ret_data=dict()
                ret_data['id']=mission_id
                ret_data['mission_class']=mission_class
                ret_data['master_money']=master_money
                ret_data['slave_money']=slave_money
                ret_data['good_num']=good_num
                ret['data']=ret
                # Query user information
                statement='select wangwang from user where username="%s"'%(username)
                res_=helper.query(statement)
                if len(res_)==0: 
                    self.write(json.dumps(ret));return
                wangwang=res_[0][0]
                statement='select keyword,good_name,master_money,slave_money,good_price from mission_class where id="%s"'%(mission_class) 
                res=helper.query(statement)
                if len(res)>0:
                    keyword=res[0][0]
                    good_name=res[0][1]
                    master_money=res[0][2]
                    slave_money=res[0][3]
                    good_price=res[0][4]
                else:
                    self.write(json.dumps(ret));return
                # Update user_order table
                statement='insert into user_order (mission_id,username,accept_time,finish_time,success,status,order_id,'+\
                        'reason,seller_username,wangwang,order_id,keyword,good_name,begin_time,end_time,master_money,slave_money,good_price)'+\
                        'values ("%s","%s","%s","","0","","","","%s","%s","","%s","%s","%s","%s","%s","%s","%s")'%(mission_id,
                                username,str(cur_timestamp),seller_username,wangwang,keyword,good_name,begin_time,
                                end_time,str(master_money),str(slave_money),str(good_price))
                res_=helper.commit(statement)
                break
            ret['code']=0
        elif code=='9':
            '''
            完成任务
            '''
            self.secure_gate()
            task_id=self.get_argument('id') # 用户接受任务的ID
            username=self.get_username()
            order_id=self.get_argument('order_id') # 淘宝订单ID
            mission_id=self.get_argument('mission_id')
            statement='select accept_time from user_order where id="%s"'%(task_id)
            accept_time=float(helper.query(statement)[0][0])
            if time.time()-accept_time<user_mission_interval:
                ret['code']=255
                ret['message']='请三分钟后前来提交任务'
                self.write(json.dumps(ret,ensure_ascii=False));return;
            # 提醒卖家后台审核
            statement='update table user_order set status="1" where order_id="%s" and username="%s"'%(task_id,username)
            res=helper.commit(statement)
            ret['code']=res
        elif code=='10':
            '''
            卖家查询订单
            op=0:查询页数，op=1：查询信息
            '''
            seller_username=self.get_argument('seller_username')
            op=int(self.get_argument('op',1))
            if op==0:
                statement='select count(*) from user_order where seller_username="%s"'%(seller_username)
                ret['count']=helper.query(statement)
                ret['page_num']=num_per_page
            else:
                page=int(self.get_argument('page',0))
                statement='select count(*) from user_order where seller_username="%s"'%(seller_username)
                ret['count']=helper.query(statement)
                ret['page_num']=num_per_page
                # Sift is used to select order status, -1 for all
                sift=self.get_argument('sift')
                if int(sift)==-1:
                    statement='mission_id,username,accept_time,finish_time,success,status,order_id,reason '+\
                        ',wangwang,keyword,good_name,begin_time,end_time'+\
                        'from user_order where seller_username="%s" order by cast(accept_time as INTEGER) desc limit %d,%d'\
                        %(seller_username,page*num_per_page,num_per_page)
                else:
                    statement='select mission_id,username,accept_time,finish_time,success,status,order_id,reason '+\
                        ',wangwang,keyword,good_name,begin_time,end_time,master_money,slave_money'+\
                        'from user_order where seller_username="%s" and status="%s" order by '+\
                        ' cast(accept_time as INTEGER) desc limit %d,%d'\
                        %(seller_username,str(sift),page*num_per_page,num_per_page)
                res=helper.query(statement)
                ret['data']=[]
                for row in res:
                    mission_id,username,accept_time,finish_time,success,status,order_id,reason,\
                        wangwang,keyword,good_name,begin_time,end_time=row
                    row_dict=dict()
                    row_dict['mission_id']=mission_id
                    row_dict['username']=username
                    row_dict['accept_time']=self.decode_stamp(accept_time)
                    row_dict['finish_time']=self.decode_stamp(finish_time)
                    row_dict['success']=success
                    row_dict['status']=self.decode_order_status(status)
                    row_dict['order_id']=order_id
                    row_dict['reason']=reason
                    row_dict['wangwang']=wangwang
                    row_dict['keyword']=keyword
                    row_dict['good_name']=good_name
                    row_dict['begin_time']=self.decode_stamp(begin_time)
                    row_dict['end_time']=self.decode_stamp(end_time)
                    row_dict['master_money']=master_money
                    row_dict['slave_money']=slave_money
                    ret['data'].append(row_dict)
                ret['code']=0
        elif code=='11':
            '''
            卖家查询资金明细
            '''
            now=datetime.datetime.now()
            time_delta=datetime.timedelta(5) # 查询近五天的资金明细
            default_begin_date=(now-time_delta).strftime('%Y%m%d')
            default_end_date=now.strftime('%Y%m%d')
            begin_date=self.get_argument('begin_date',default_begin_date)
            end_date=self.get_argument('end_date',default_end_date)
            # Change date to timestamp
            begin_date=self.decode_datetime(begin_date)
            end_date=self.decode_datetime(end_date)
            statement='select master_money,slave_money,good_price,finish_time'+\
                    'from user_order where seller_username="%s" and status="2" order by cast(finish_time as INTEGER)'\
                    %(seller_username)
            res=helper.query(statement)
            ret['data']=dict()
            ret['data']['master_money']=[]
            ret['data']['slave_money']=[]
            ret['data']['good_price']=[]
            ret['data']['finish_time']=[]
            for row in res:
                ret['data']['master_money'].append(row[0])
                ret['data']['slave_money'].append(row[1])
                ret['data']['good_price'].append(row[2])
                ret['data']['finish_time'].append(row[3])
            ret['code']=0
        elif code=='12':
            '''
            用户查询订单
            '''
            self.secure_gate()
            username=self.get_username() 
            op=int(self.get_argument('op',1))
            if op==0:
                statement='select count(*) from user_order where seller_username="%s" and username="%s"'%(seller_username,username)
                ret['count']=helper.query(statement)
                ret['page_num']=num_per_page
            else:
                page=int(self.get_argument('page',0))
                statement='select count(*) from user_order where seller_username="%s" and username="%s"'%(seller_username,username)
                ret['count']=helper.query(statement)
                ret['page_num']=num_per_page

                # Sift is used to select order status, -1 for all
                sift=self.get_argument('sift')
                if int(sift)==-1:
                    statement='mission_id,username,accept_time,finish_time,success,status,order_id,reason '+\
                        ',wangwang,keyword,good_name,begin_time,end_time'+\
                        'from user_order where seller_username="%s" and username="%s" order by  cast(accept_time as INTEGER) desc limit %d,%d'\
                        %(seller_username,username,page*num_per_page,num_per_page)
                else:
                    statement='select mission_id,username,accept_time,finish_time,success,status,order_id,reason '+\
                        ',wangwang,keyword,good_name,begin_time,end_time,master_money,slave_money'+\
                        'from user_order where seller_username="%s" and username="%s" and status="%s" order by '+\
                        ' cast(accept_time as INTEGER) desc limit %d,%d'\
                        %(seller_username,username,str(sift),page*num_per_page,num_per_page)
                res=helper.query(statement)
                ret['data']=[]
                for row in res:
                    mission_id,username,accept_time,finish_time,success,status,order_id,reason,\
                        wangwang,keyword,good_name,begin_time,end_time=row
                    row_dict=dict()
                    row_dict['mission_id']=mission_id
                    row_dict['username']=username
                    row_dict['accept_time']=self.decode_stamp(accept_time)
                    row_dict['finish_time']=self.decode_stamp(finish_time)
                    row_dict['success']=success
                    row_dict['status']=self.decode_order_status(status)
                    row_dict['order_id']=order_id
                    row_dict['reason']=reason
                    row_dict['wangwang']=wangwang
                    row_dict['keyword']=keyword
                    row_dict['good_name']=good_name
                    row_dict['begin_time']=self.decode_stamp(begin_time)
                    row_dict['end_time']=self.decode_stamp(end_time)
                    row_dict['master_money']=master_money
                    row_dict['slave_money']=slave_money
                    ret['data'].append(row_dict)
                ret['code']=0

        elif code=='13':
            '''
            用户查询资金明细
            '''
            self.secure_gate()
            username=self.get_username()
            now=datetime.datetime.now()
            time_delta=datetime.timedelta(5) # 查询近五天的资金明细
            default_begin_date=(now-time_delta).strftime('%Y%m%d')
            default_end_date=now.strftime('%Y%m%d')
            begin_date=self.get_argument('begin_date',default_begin_date)
            end_date=self.get_argument('end_date',default_end_date)
            # Change date to timestamp
            begin_date=self.decode_datetime(begin_date)
            end_date=self.decode_datetime(end_date)
            statement='select master_money,slave_money,good_price,finish_time'+\
                    'from user_order where seller_username="%s" and status="2" and username="%s" order by '+\
                    ' cast(finish_time as INTEGER)'\
                    %(seller_username,username)
            res=helper.query(statement)
            ret['data']=dict()
            ret['data']['master_money']=[]
            ret['data']['slave_money']=[]
            ret['data']['good_price']=[]
            ret['data']['finish_time']=[]
            for row in res:
                ret['data']['master_money'].append(row[0])
                ret['data']['slave_money'].append(row[1])
                ret['data']['good_price'].append(row[2])
                ret['data']['finish_time'].append(row[3])
            ret['code']=0
        elif code=='14':
            '''
            查询用户信息
            @Deprecated
            @NotImplemented
            '''
            wechat_id=self.get_argument('wechat_id')
        elif code=='15':
            '''
            用户注册
            '''
            wechat_id=self.get_argument('wechat_id','')
            # whether use already exist
            statement='select id,status from user where wechat_id="%s"'%(wechat_id)
            res=helper.query(statement)
            if len(res)>0:
                ret['message']='用户已存在'
                self.write(json.dumps(ret,ensure_ascii=False));return
            inviter_id=self.get_argument('inviter_id')
            age=self.get_argument('age')
            gender=self.get_argument('gender')
            wangwang=self.get_argument('wangwang','')
            trading_image=''
            if 'images' in self.request.files:
                file_metas=self.request.files['images']
                for meta in file_metas:
                    filename=meta['filename'].replace(' ','')
                    # Build file path
                    prefix='image/'+seller_username+'/'
                    if not os.path.exists(prefix):
                        os.mkdir(prefix)
                    new_file_name=prefix+filename
                    if os.path.exists(new_file_name):
                        filename=str(random.randint(0,10000))+filename
                        new_file_name=prefix+filename
                    with open(new_file_name,'wb') as up:
                        up.write(meta['body'])
                    trading_image=new_file_name
            statement='insert into user (wechat_id,inviter_id,age,gender,wangwang,trading_image) values ("%s","%s","%s","%s","%s","%s")'\
                    %(wechat_id,inviter_id,age,gender,wangwang,trading_image)
            res=helper.commit(statement)
            print('[DEBUG] user register res:',res)
            ret['code']=res
        elif code=='16':
            '''
            店铺管理，查询店铺数量，增加删除店铺
            op 0:查询所有店铺
            op 1:增加店铺
            op 2:删除店铺
            op 3:更改店铺间隔
            '''
            op=self.get_argument('op')
            helper=DBHelper(1)
            statement='select shop,mission_interval from shops where seller_username="%s"'%(seller_username)
            #statement='select shops from seller where seller_username="%s"'%(seller_username)
            res=helper.query(statement)
            if op=='0':
                ret['data']=res
                ret['code']=0
                '''
                if len(res)>0 and res[0][0]!=None and res[0][0].strip()!='':
                    shops=res[0][0].strip().split()
                    ret['data']=shops
                    ret['code']=0
                '''
            elif op=='1':
                shop_name=self.get_argument('shop_name')
                interval=self.get_argument('interval')
                statement='insert into shops (seller_username,shop,mission_interval) values ("%s","%s","%s")'\
                        %(seller_username,shop_name,interval)
                ret['code']=helper.commit(statement)
                '''
                if res[0][0]==None:
                    shops=shop_name
                else:
                    shops=res[0][0]+' '+shop_name
                statement='update seller set shops="%s" where seller_username="%s"'\
                        %(shops,seller_username)
                helper.commit(statement)
                # 调整数据库
                statement='insert into shops (seller_username,shop,mission_interval) values '+\
                        '("%s","%s","3")'%(seller_username,shop_name)
                ret['code']=helper.commit(statement)
                '''
            elif op=='2':
                shop_name=self.get_argument('shop_name')
                statement='delete from shops where seller_username="%s" and shop="%s"'%(seller_username,shop_name)
                #print(statement)
                ret['code']=helper.commit(statement)
                '''
                shop_name=self.get_argument('shop_name')
                if res[0][0]!=None and res[0][0].strip()!='':
                    shops=res[0][0].strip().split()
                    if shop_name in shops:
                        shops.remove(shop_name)
                        # Build new shops
                        new_shops=''
                        for s in shops:
                            new_shops+=s+' '
                        new_shops=new_shops[:-1]
                        statement='update seller set shops="%s" where seller_username="%s"'\
                            %(new_shops,seller_username)
                        res=helper.query(statement)
                        # Delete from table shops
                        statement='delete from shops where seller_username="%s" and shop="%s"'\
                                %(seller_username,shop_name)
                        res=helper.commit(statement)
                        ret['code']=res
                '''
            elif op=='3':
                shop_name=self.get_argument('shop_name')
                mission_interval=self.get_argument('mission_interval')
                statement='update shops set mission_interval="%s" where seller_username="%s" and shop="%s"'\
                        %(mission_interval,seller_username,shop_name)
                #print(statement)
                ret['code']=helper.commit(statement)
            else:
                pass
        elif code=='17':
            '''
            用户提现
            '''
            # TODO-B: 当数额较大时增加安全校验
            # 查询提现时间
            statement='select setting from seller where username="%s"'%(seller_username)
            setting=helper.query(statement)[0][0]
            cash_begin_hour,cash_begin_minute=0,0
            cash_end_hour,cash_end_minute=24,60
            if setting!=None and setting!='':
                setting=json.loads(setting)
                cash_begin_hour,cash_begin_minute=int(setting['cash_begin_time'][:2]),int(setting['cash_begin_time'][3:5])
                cash_end_hour,cash_end_minute=int(setting['cash_end_time'][:2]),int(setting['cash_end_time'][3:5])
            now=datetime.datetime.now()
            cur_hour,cur_minute=now.hour,now.minute
            if cur_hour<cash_begin_hour or cur_hour>cash_end_hour:
                self.reply();return
            if (cur_hour==cash_begin_hour and cur_minute<cash_begin_minute) or \
                    (cur_hour==cash_end_hour and cur_minute>cash_end_minute):
                self.reply();return
            username=self.get_username()
            op=self.get_argument('op')
            # op=0: 查询余额，op=1:提现
            # Query user account
            statement='select id,cash_op,cash_left,detail,create_date '+\
                    'from cash_order where username="%s" order by id desc limit 1'\
                    %(username)
            res=helper.query(statement)
            if len(res)>0 and res[0][0]!=None:
                cash_id,cash_op,cash_left,detail,create_date=res[0]
                cash_left=float(cash_left)
                if op=='0':
                    ret['data']=cash_left
                    ret['code']=0
                elif op=='1':
                    money=float(self.get_argument('money'))
                    if money>0 and cash_left>money:
                        #将数据写入数据库，提交提现
                        cash_op='提现'
                        detail='正常提现'
                        cash_left=cash_left-money
                        cash_callback=self.pay_cash(money)
                        redpack_sn=cash_callback['redpack_sn']
                        extra=dict()
                        extra['redpack_sn']=redpack_sn
                        extra=json.dumps(extra)
                        statement='insert into cash_order (cash_op,cash_left,detail,create_date,extra) values ("%s","%.4f","%s",now(),"%s")'\
                                %(cash_op,cash_left,detail,extra)
                        res=helper.commit(statement)
                        ret['code']=res
                        ret['data']=cash_callback['redpackurl']
                else:
                    pass
        elif code=='18':
            '''
            查询用户状态
            '''
            username=self.get_username()
            if user_name==None:
                ret['code']=1
                ret['message']='用户未注册'
            else:
                ret['code']=0
                ret['message']='用户已注册'
        elif code=='19':
            '''
            卖家确认订单
            '''
            username=self.get_username()
            order_id=self.get_argument('order_id')
            # Step 1. 更改订单状态
            statement='update user_order set status="2" where id="%s"'%(order_id)
            res=helper.commit(statement)
            # Step 2. 查询用户身份
            statement='select role,master_id,master_wechat_id from user where username="%s"'%(username) 
            res=helper.query(statement)
            role=int(res[0][0])
            master_id=res[0][1]
            master_wechat=res[0][2]
            # 查询订单状态
            statement='select mission_id from user_order where id="%s"'%(order_id)
            mission_id=helper.query(statement)[0][0]
            statement='select good_price,master_money,slave_money from mission_object where id="%s"'%(mission_id)
            good_price,master_money,slave_money=helper.query(statement)[0]
            if role<3:
                self.write(json.dumps(ret,ensure_ascii=False));return;
            # Step 3. 查询用户现金账户并生成现金交易订单
            if role==3:
                # 徒弟账户
                statement='select id,cash_op,cash_left,detail,create_date '+\
                    'from cash_order where username="%s" order by id desc limit 1'\
                    %(username)
                res=helper.query(statement)
                slave_cash_left=float(res[0][2])
                slave_cash_op=good_price+slave_money
                slave_cash_left+=good_price+slave_money
                statement='insert into cash_order (username,cash_op,cash_left,detail,create_date)'+\
                    'values("%s","%f","%f","完成任务",now())'\
                    %(username,slave_cash_op,slave_cash_left)
                helper.commit(statement)
                # 师傅账户
                statement='select id,cash_op,cash_left,detail,create_date '+\
                    'from cash_order where username="%s" order by id desc limit 1'\
                    %(master_id)
                master_cash_left=float(helper.query(statement)[0][2])
                master_cash_op=master_money
                master_cash_left+=master_cash_op
                statement='insert into cash_order (username,cash_op,cash_left,detail,create_date)'+\
                    'values("%s","%f","%f","完成任务",now())'\
                    %(master_id,master_cash_op,master_cash_left)
                helper.commit(statement)
            elif role==4:
                # 师傅账户
                statement='select id,cash_op,cash_left,detail,create_date '+\
                    'from cash_order where username="%s" order by id desc limit 1'\
                    %(username)
                res=helper.query(statement)
                master_cash_left=float(res[0][2])
                master_cash_op=good_price+slave_money+master_money
                master_cash_left+=mast
                statement='insert into cash_order (username,cash_op,cash_left,detail,create_date)'+\
                    'values("%s","%f","%f","完成任务",now())'\
                    %(username,master_cash_op,master_cash_left)
                helper.commit(statement)
        elif code=='20':
            '''
            卖家审核新手身份
            0审核中，1卖家审核完毕，2师傅审核完毕，3徒弟，4师傅
            '''
            username=self.get_username()
            # Query current user status
            statement='select status from user where username="%s"'%(username)
            status=int(helper.query(statement)[0][0])
            if status==0:
                status=1
            elif status==2:
                status=3
            else:
                self.write(json.dumps(ret));return
            statement='update user set status="%d" where username="%s"'%(status,username)
            ret['code']=helper.commit(statement)
        elif code=='21':
            '''
            师傅审核新手身份
            '''
            username=self.get_username()
            # Query current user status
            statement='select status from user where username="%s"'%(username)
            status=int(helper.query(statement)[0][0])
            if status==0:
                status=2
            elif status==1:
                status=3
            else:
                self.write(json.dumps(ret));return
            statement='update user set status="%d" where username="%s"'%(status,username)
            ret['code']=helper.commit(statement)

        elif code=='22':
            '''
            卖家拉黑用户
            '''
            username=self.get_username()
            statement='update user set blacklist=1 where id="%s"'%(username)
            ret['code']=helper.commit(statement)
        elif code=='23':
            '''
            师傅拉黑用户
            '''
            username=self.get_username()
            statement='update user set blacklist=1 where id="%s"'%(username)
            ret['code']=helper.commit(statement)
        elif code=='24':
            '''
            卖家用户管理，查询用户
            '''
            op=int(self.get_argument('op',1))
            if op==0:
                statement='select count(*) from user where seller_username="%s" and role>-1'%(seller_username)
                ret['count']=helper.query(statement)
                ret['page_num']=num_per_page

            else:
                statement='select count(*) from user where seller_username="%s" and role>=0'%(seller_username)
                ret['count']=helper.query(statement)
                ret['page_num']=num_per_page
                page=int(self.get_argument('page',0))
                statement='select id,wechat_id,inviter_id,age,gender,wangwang,create_date,role,trading_image,blacklist,master_id '+\
                        'from user where seller_username="%s"  order by create_date desc limit %d,%d '%(seller_username,page*num_per_page,num_per_page)
                res=helper.query(statement)
                ret['data']=[]
                ret['code']=0
                if res==None:
                    res=[]
                for row in res:
                    row_dict=dict()
                    row_dict['id']=row[0]
                    row_dict['wechat_id']=row[1]
                    row_dict['inviter_id']=row[2]
                    row_dict['age']=row[3]
                    row_dict['gender']=row[4]
                    row_dict['wangwang']=row[5]
                    row_dict['create_date']=row[6].strftime("%Y%m%d-%H%M")
                    row_dict['role']=self.decode_role(row[7])
                    row_dict['trading_image']=row[8]
                    row_dict['blacklist']=self.decode_blacklist(row[9])
                    row_dict['master_id']=row[9]
                    ret['data'].append(row_dict)
        elif code=='25':
            '''
            师傅用户管理，查询用户
            '''
            master_id=self.get_argument('master_id')
            statement='select id,wechat_id,inviter_id,age,gender,wangwang,create_date,role,trading_image,blacklist'+\
                    'from user where master_id="%s" and role>=0 order by order by create_date desc'%(master_id)
            res=helper.query(statement)
            ret['data']=[]
            ret['code']=0
            for row in res:
                row_dict=dict()
                row_dict['id']=row[0]
                row_dict['wechat_id']=row[1]
                row_dict['inviter_id']=row[2]
                row_dict['age']=row[3]
                row_dict['gender']=row[4]
                row_dict['wangwang']=row[5]
                row_dict['create_date']=row[6].strftime("%Y%m%d-%H%M")
                row_dict['role']=self.decode_role(row[7])
                row_dict['trading_image']=row[8]
                row_dict['blacklist']=self.decode_blacklist(row[9])
                ret['data'].append(row_dict)
        elif code=='26':
            '''
            将徒弟升级到师傅
            '''
            username=self.get_username()
            statement='update user set role="4" where id="%s"'%(username)
            ret['code']=helper.commit(statement)
        elif code=='27':
            '''
            从微信code获取微信openID
            '''
            statement='select appid,secret from seller where username="%s"'%(seller_username)
            res=helper.query(statement)
            wechat_code=self.get_argument('wechat_code')
            appid=res[0][0]
            secret=res[0][1]
            ret['data']=self.get_open_id(wechat_code,appid,secret)
            ret['code']=0
        elif code=='28':
            '''
            商家登陆
            '''
            passwd=self.get_argument('passwd')
            statement='select passwd from seller where username="%s"'%(seller_username)
            res=helper.query(statement)
            if len(res)>0 and res[0][0]==passwd:
                ret['code']=0
                ret['message']='登录成功'
            else:
                ret['code']=255
                ret['message']='登录失败'
        elif code=='29':
            '''
            设置用户执行任务间隔天数
            '''
            wechat_id=self.get_argument('wechat_id')
            mission_interval=self.get_argument('mission_interval')
            statement='update user set mission_interval="%s" where wechat_id="%s"'%(mission_interval,wechat_id)
            ret['code']=helper.commit(statement)
        elif code=='30':
            '''
            为用户添加备注信息
            '''
            wechat_id=self.get_argument('wechat_id')
            extra=self.get_argument('extra')
            statement='update user set extra="%s" where wechat_id="%s"'%(extra,wechat_id)
            ret['code']=helper.commit(statement)
        elif code=='31':
            '''
            卖家设置用户提现时间段
            格式如下：17:00
            '''
            statement='select setting from seller where username="%s"'%(seller_username)
            setting=helper.query(statement)[0][0]
            if setting==None or setting=='':
                data=dict()
            else:
                data=json.loads(setting)
            begin_time=self.get_argument('begin_time')
            end_time=self.get_argument('end_time')
            data['cash_begin_time']=begin_time
            data['cash_end_time']=end_time
            data=json.dumps(data,ensure_ascii=False)
            statement='update seller set setting="%s" where username="%s"'%(data,seller_username)
            ret['code']=helper.commit(statement)
        elif code=='32':
            '''
            查询提现时间段
            '''
            statement='select setting from seller where username="%s"'%(seller_username)
            setting=helper.query(statement)[0][0]
            if setting==None or setting=='':
                data=dict()
            else:
                data=json.loads(setting)
            begin_time=self.get_argument('begin_time')
            end_time=self.get_argument('end_time')
            ret['code']=0
            ret['begin_time']=begin_time
            ret['end_time']=end_time
        elif code=='33':
            '''
            查询或设置公告
            op=0:查询 op=1:设置
            '''
            op=int(self.get_argument('op',0))
            if op==0:
                statement='select notice from seller where username="%s"'%(seller_username)
                ret['code']=0
                ret['data']=helper.query(statement)[0][0]
            elif op==1:
                notice=self.get_argument('notice')
                statement='update seller set notice="%s" where username="%s"'%(notice,seller_username)
                ret['code']=helper.commit(statement)
            else:
                pass
        elif code=='34':
            '''
            拒绝用户申请
            '''
            username=self.get_username()
            statement='update user set role="-1" where id="%s"'%(username)
            ret['code']=helper.commit(statement)
        else:
            pass
        self.set_header("Access-Control-Allow-Origin", "*") # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.write(json.dumps(ret,ensure_ascii=False))

    def get_shop_dict(self,x,interval=None):
        '''
        id,mission_id,accept_time,finish_time,shop
        '''
        helper=DBHelper()
        seller_username=self.get_argument('seller_username')
        ret=set()
        if len(x)==0:
            return ret
        now=time.time()
        shop_cache=dict()
        for row in x:
            order_id,mission_id,accept_time,finish_time,shop=row
            accept_time=float(accept_time)
            finish_time=float(finish_time)
            if shop not in shop_dict:
                # Query shop interval
                statement='select mission_interval from shops where seller_username="%s" and shop="%s"'\
                        %(seller_username,shop)
                res=helper.query(statement)
                shop_interval=res[0][0]
                if shop_interval==None:
                    continue
                shop_cache[shop]=int(shop_interval)
            shop_interval=shop_cache[shop]
            if interval==None:
                if now-accept_time<shop_interval*24*3600:
                    ret.add(shop)
            else:
                if now-accept_time<interval*24*3600:
                    ret.add(shop)
        return ret

    def decode_blacklist(self,x):
        x=int(x)
        if x==0:
            return "正常"
        else:
            return "被拉黑"

    def decode_stamp(self,x):
        x=float(x)
        return datetime.datetime.fromtimestamp(x).strftime('%Y%m%d-%H%M')

    def decode_datetime(self,x):
        '''
        Decode a date string to timestamp format
        '''
        if '-' in x:
            x=datetime.datetime.strptime(x,"%Y%m%d-%H%M")
        else:
            x=datetime.datetime.strptime(x,"%Y%m%d")
        return str(x.timestamp())
  
    def decode_role(self,role):
        role=int(role)
        if role==0:
            return '审核中'
        elif role==1:
            return '卖家审核完毕'
        elif role==2:
            return '师傅审核完毕'
        elif role==3:
            return '徒弟'
        elif role==4:
            return '师傅'
        else:
            return '出错'

    def get_username(self):
        wechat_id=self.get_argument('wechat_id')
        helper=DBHelper()
        statement='select id from user where wechat_id="%s"'%(wechat_id)
        res=helper.query(statement)
        if len(res)>0 and res[0][0]!=None:
            return res[0][0]
        else:
            return None

    def decode_order_status(self,x):
        if x==None:
            return '状态错误'
        x=int(x)
        if x==0:
            return '任务进行中'
        elif x==1:
            return '任务已提交'
        elif x==2:
            return '审核成功'
        elif x==3:
            return '审核失败'
        elif x==4:
            return '任务失败'
        else:
            return '参数错误'
    def pay_cash(self,money,open_id=None):
        '''
        Get user id and pay him.
        #返回值是一个dict，key“redpackurl”是红包链接
        '''
        if open_id==None:
            open_id=self.get_argument('wechat_id')
        method="jfy.redpacks.send"
        jsdict_1=OrderedDict();
        jsdict_1['appkey']=myappkey
        jsdict_1['method']=method
        jsdict_1['openid']=open_id
        jsdict_1['money']=money
        jsonsend_bytes=urllib.parse.urlencode(jsdict_1).encode('utf-8')
        response= urllib.request.urlopen(apiurl,jsonsend_bytes).read().decode('utf-8')
        dict=json.loads(response)
        return dict;

    def get_open_id(self,code,appid='wx1c61776edae08975',secret='15625151323fe35cccd702c5cf987e83'):
        apiurl="https://api.weixin.qq.com/sns/oauth2/access_token?appid="+appid+"&secret="+secret+"&code="+code+"&grant_type=authorization_code"
        response= urllib.request.urlopen(apiurl).read().decode('utf-8')
        dict=json.loads(response)
        for key in dict:
            if key == 'openid':
               # print (dict['openid'])
                return dict['openid']
   
    def reply(self):
        self.write(json.dumps({"code":255}))

    def checkredpack(self,redpack_sn):
        #查询红包，唯一参数 红包编号，redpack_sn
        method="jfy.redpacks.get"
        jsdict_2=OrderedDict();
        jsdict_2['appkey']=myappkey
        jsdict_2['method']=method
        jsdict_2['redpack_sn']=redpack_sn
        jsoncheck=json.dumps(jsdict_2)
        response= urllib.request.urlopen(apiurl,jsoncheck).read().decode('utf-8')
        dict=json.loads(response)
        return dict;
