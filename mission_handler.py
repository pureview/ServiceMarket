import tornado.ioloop
import tornado.web
import sys
import json
import os
import random
import time
import requests
import datetime
import logging
from collections import OrderedDict
import urllib.request
import urllib.parse
import multiprocessing
from util.db import *
from util.logger import *
from util.message_util import *
#from util.pay_util import *
# BUG:预期等待时间不正确
pay_url_prefix='http://work-flow.cn:8964/pay_cash'
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
        ############### Config #################
        num_per_page=20
        user_mission_interval=60*3 # 任务倒计时时间
        shop_interval_days=3 
        user_timeout=30*60 # 任务过时时间
        mission_heartbeat_interval=20 # 任务订单刷新间隔
        self.mission_heartbeat_interval=20 # 任务订单刷新间隔
        push_heartbeat_interval=3600
        self.push_heartbeat_interval=3600 # 推送刷新间隔
        ########################################
        ret=dict()
        ret['code']=255
        code=self.get_argument('code')
        seller_username=self.get_argument('seller_username','test_seller')
        helper=DBHelper()
        print(self.request.body)
        if code=='0':
            # 发布任务
            # 获取图片
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
                self.reply(ret);return
            # 如果是多个，请用空格分割
            mission_nums=self.get_argument('mission_nums')
            keywords=self.get_argument('keywords')
            # 常规参数
            status=0
            sort=self.get_argument('sort')
            shop=self.get_argument('shop')
            begin_time=self.date2stamp(self.get_argument('begin_time'))
            end_time=self.date2stamp(self.get_argument('end_time'))
            master_money=float(self.get_argument('master_money',0))
            slave_money=float(self.get_argument('slave_money'))
            allow=int(self.get_argument('allow'))
            good_num=int(self.get_argument('good_num'))
            price_lower=float(self.get_argument('price_lower',0))
            price_higher=float(self.get_argument('price_higher',0))
            good_name=self.get_argument('good_name')
            good_price=float(self.get_argument('good_price'))
            good_place=self.get_argument('good_place','')
            cash_on_delivery=int(self.get_argument('cash_on_delivery',0))
            extra=self.get_argument('extra','')
            last_timestamp=time.time()-3600*24
            group_id=0
            statement='insert into mission (seller_username,mission_nums,keywords,status,sort,shop,begin_time,end_time,master_money,'+\
                    'slave_money,allow,good_num,price_lower,price_higher,good_name,good_price,create_date,task_image,last_timestamp,group_id,good_place,cash_on_delivery,extra)'+\
                    'values("%s","%s","%s","%d","%s","%s","%f","%f","%f","%f","%d","%d","%f",%f,"%s",%f,now(),\'%s\',"%f","%f","%s",%d,"%s")'\
                    %(seller_username,mission_nums,keywords,status,sort,shop,begin_time,end_time,master_money,slave_money,allow,
                            good_num,price_lower,price_higher,good_name,good_price,task_image,last_timestamp,group_id,good_place,cash_on_delivery,extra)
            helper.commit(statement)
            mission_id=helper.query('select last_insert_id()')[0][0]
            # 加载到用户任务列表
            mission_nums_p=list(map(int,mission_nums.split(' ')))
            keywords_p=keywords.split(' ')
            mission_num_sum=sum(mission_nums_p)
            keywords_pool=[]
            for i in range(len(mission_nums_p)):
                keywords_pool.extend([keywords_p[i]]*mission_nums_p[i])
            shuffle_begin=time.time()
            print('Begin shuffle')
            random.shuffle(keywords_pool)
            shuffle_end=time.time()
            print('End shuffle,',shuffle_end-shuffle_begin)
            # 计算每个任务的时间和关键词
            mission_interval=(end_time-begin_time)/mission_num_sum
            count_order_begin=time.time()
            for i in range(mission_num_sum):
                # Sample keyword
                # TODO: 优化随机性能
                sys.stdout.write('Processing %d of %d orders\r'%(i,mission_num_sum))
                sys.stdout.flush()
                keyword=keywords_pool[i]
                order_begin_time=begin_time+mission_interval*i
                statement='insert into user_order (mission_id,status,seller_username,keyword,good_name,begin_time,end_time,master_money,slave_money,good_price,shop,order_begin_time ) values '+'\
                        ("%s","-2","%s","%s","%s","%f","%f","%s","%s","%s","%s","%f")'\
                        %(mission_id,seller_username,keyword,good_name,begin_time,end_time,str(master_money),str(slave_money),str(good_price),shop,order_begin_time)
                helper.commit(statement)
            count_order_end=time.time()
            print('\nProcessing order use %fs'%(count_order_end-count_order_begin))
            res=helper.commit(statement)
            ret['code']=res
        elif code=='1':
            '''
            用户管理，更改任务间隔天数
            '''
            username=self.get_username()
            ret['code']=0
            mission_interval=self.get_argument('mission_interval') 
            helper.commit('update user set mission_interval='+str(mission_interval)+' where id='+str(username))
            extra=self.get_argument('extra',0)
            if extra!=0:
                statement='update user set extra="%s" where id="%s"'%(extra,username)
                helper.commit(statement)

        elif code=='2':
            '''
            获取任务列表
            '''
            helper=DBHelper(1)
            num_per_page=int(num_per_page)
            page=int(self.get_argument('page',-1))
            statement='select count(*) from mission where seller_username="%s"'%(seller_username)
            begin_time=self.get_argument('begin_time',None)
            end_time=self.get_argument('end_time',None)
            cur_datetime=datetime.datetime.now()
            default_begin_time=datetime.datetime(cur_datetime.year,cur_datetime.month,cur_datetime.day,0,0).timestamp()
            default_end_time=datetime.datetime(cur_datetime.year,cur_datetime.month,cur_datetime.day,23,59).timestamp()
            if begin_time!=None and end_time!=None:
                begin_time=self.date2stamp(begin_time)
                end_time=self.date2stamp(end_time)
            else:
                begin_time=default_begin_time
                end_time=default_end_time
            time_statement=' begin_time>%f and begin_time<%f  and '%(begin_time,end_time)
            ret['count']=helper.query(statement)
            ret['page_num']=num_per_page
            ret['code']=0 
            if page==-1:
                # 选择所有数据，将分段加载交给前端
                statement='select * from mission where '+time_statement+\
                        'seller_username="%s" order by create_date desc '%(seller_username)
            else:
                statement='select * from mission where '+time_statement+\
                        'seller_username="%s" order by create_date desc limit %d,%d'%(seller_username,page*num_per_page,num_per_page)
            res=helper.query(statement)
            # 更新任务状态
            now=time.time()
            ret['data']=[]
            for row in res:
                if row['end_time']<now:
                    statement='update mission set status=2 where id="%d"'%(row['id'])
                    helper.commit(statement)
                row['begin_time']=self.decode_stamp(row['begin_time'])
                row['end_time']=self.decode_stamp(row['end_time'])
                row.pop('create_date')
                row['mission_num']=str(row['mission_num'])
                ret['data'].append(row)
        elif code=='3':
            '''
            删除任务
            '''
            mission_id=self.get_argument('id')
            # 删除任务列表
            statement='delete from mission where id='+mission_id
            helper.commit(statement)
            # 删除订单列表
            statement='delete from user_order where mission_id='+mission_id
            res=helper.commit(statement)
            ret['code']=res
        elif code=='4':
            '''
            根据任务ID查询任务信息
            '''
            helper=DBHelper(1)
            mission_id=self.get_argument('mission_id')
            res=helper.query('select * from mission where id='+mission_id)
            if len(res)>0:
                ret['code']=0
                for row in res:
                    row['begin_time']=self.decode_stamp(row['begin_time'])
                    row['end_time']=self.decode_stamp(row['end_time'])
                    row['create_date']=row['create_date'].strftime('%Y%m%d-%H%M')
                ret['data']=res
        elif code=='5':
            '''
            取消拉黑用户
            '''
            username=self.get_argument('username')
            ret['code']=helper.commit('update user set blacklist=0 where id='+username)
        elif code=='6':
            '''
            返回同时发布的一组任务
            '''
            helper=DBHelper(1)
            mission_id=self.get_argument('mission_id')
            res=helper.query('select * from mission where id='+mission_id)
            if len(res)==0:
                ret['message']='任务不存在'
                self.reply(ret);return
            ret['code']=0
            res[0].pop('create_date')
            ret['data']=res[0]
        elif code=='7':
            # 取消任务
            mission_id=self.get_argument('id')
            # 更改任务状态
            statement='update mission set status=1 where id='+mission_id
            helper.commit(statement)
            # 更改订单状态
            statement='update user_order set status=5 where mission_id=%s and status<0'%(mission_id)
            res=helper.commit(statement)
            ret['code']=res
        elif code=='8':
            '''
            申请任务或者获取已有的任务
            业务逻辑：查询当前可用任务，如果可用，更新状态，返回一个订单，否则返回没有订单
            警告：相比于之前的版本，必须多传一个参数叫mission_id，根据这个ID来申请任务
            ''' 
            self.secure_gate()
            username=self.get_username()
            wechat_id=self.get_argument('wechat_id')
            user_order_id=self.get_argument('user_order_id',None)
            mission_id=self.get_argument('mission_id',None)
            ret['data']=dict()
            helper=DBHelper(1)            
            if user_order_id==None:
                # 申请新的任务
                # 校验合法性
                helper=DBHelper()
                # Query active mission
                statement='select id from user_order where username="%s" and status=0'%(username)
                res=helper.query(statement)
                if len(res)>0:
                    ret['message']='请在任务管理中完成已有的任务'
                    self.reply(ret);return
                # Query user's identity
                statement='select role,blacklist,mission_interval,last_timestamp from user where wechat_id="%s"'%(wechat_id)
                res=helper.query(statement)
                if len(res)>0:
                    role,black_list,mission_interval,last_timestamp=res[0]
                    if (black_list!=None and black_list!=0) or role==None or role==0:
                        ret['message']='您无法做任务'
                        self.reply(ret);return
                else:
                    print(statement)
                    ret['message']='您还未注册'
                    self.reply(ret);return
                user_interval=res[0][2]
                if user_interval==None:
                    user_interval=7
                user_last_timestamp=res[0][3]
                cur_timestamp=time.time()
                if cur_timestamp-user_last_timestamp<user_interval*24*3600:
                    ret['message']='每%d天只能做一次任务'%(user_interval)
                    self.reply(ret);return
                # 申请任务
                helper=DBHelper(1)
                statement='select * from user_order where status=-1 limit 1'
                res=helper.query(statement)
                if len(res)>0:
                    # 只取第一个任务，
                    # 返回获取任务成功
                    ret['code']=0
                    ret['data']=res[0]
                    # 更改订单状态
                    statement='update user_order set status=0,username="%s",accept_time="%s" where id='%(username,str(time.time()))+str(res[0]['id'])
                    print('更改订单状态:',statement)
                    helper.commit(statement)
                    # 更改用户状态
                    statement='update user set last_timestamp=%f,pushed=0 where id="%s"'%(time.time(),username)
                    helper.commit(statement)
                    mission_id=res[0]['mission_id']
                    user_order_id=res[0]['id']
                    time_left=user_timeout
                    keyword=res[0]['keyword']
                    open_id=self.get_argument('wechat_id')
                    now=datetime.datetime.now().strftime('%Y%m%d-%H%M')
                    mission_url='http://work-flow.cn/static/wechat/html/taskDetail.html?id='+str(user_order_id)
                    push_take_order(open_id,user_order_id,now,mission_url)

                else:
                    ret['code']=255
                    ret['message']='任务被抢走了'
                    self.reply(ret);return
            else:
                # First, query mission id
                res=helper.query('select * from user_order where id="%s"'%(user_order_id))
                if len(res)==0:
                    print('无法从user_order_id找到任务',statement)
                    ret['message']='任务不存在'
                    self.reply(ret);return
                accept_time=res[0]['accept_time']
                mission_id=res[0]['mission_id']
                keyword=res[0]['keyword']
                if accept_time!=None:
                    time_left=user_timeout-time.time()+float(accept_time)
                    if time_left<0:
                        time_left=0
                    if time_left==0:
                        ret['message']='任务超时'
                        self.reply(ret);return
            # 根据任务ID查询相关信息
            statement='select * from mission where id='+str(mission_id)
            res=helper.query(statement)
            if len(res)==0:
                ret['message']='找不到任务'
                self.reply(ret);return
            # 根据任务ID查询
            ret['data']=res[0]
            ret['data']['keyword']=keyword
            ret['data'].pop('create_date')
            # Query user information
            statement='select wangwang from user where id="%s"'%(username)
            res_=helper.query(statement)
            if len(res_)==0: 
                ret['message']='查询不到旺旺号'
                self.reply(ret);return
            wangwang=res_[0]['wangwang']
            ret['code']=0
            ret['data']['time_left']=time_left
            ret['data']['user_order_id']=user_order_id            
            print(ret)
                
        elif code=='9':
            '''
            完成任务
            '''
            print('完成任务:',self.request.body)
            self.secure_gate()
            user_order_id=self.get_argument('user_order_id') # 用户接受任务的ID
            username=self.get_username()
            order_id=self.get_argument('order_id') # 淘宝订单ID
            wangwang=self.get_argument('wangwang',None)
            #mission_id=self.get_argument('mission_id')
            statement='select accept_time,mission_id,status from user_order where id="%s"'%(user_order_id)
            res=helper.query(statement)
            accept_time=float(res[0][0])
            status=res[0][2]
            if status!=0:
                ret['message']='禁止多次提交任务'
                self.reply(ret);return
            print(accept_time,time.time()-accept_time)
            mission_id=res[0][1]
            if time.time()-accept_time<user_mission_interval:
                ret['code']=255
                ret['message']='请三分钟后前来提交任务'
                print(json.dumps(ret,ensure_ascii=False))
                self.reply(ret);return;
            if time.time()-accept_time>user_timeout:
                ret['code']=255
                statement='update user_order set status="4" where id="%s" and username="%s"'%(user_order_id,username)
                helper.commit(statement)
                # 任务失败，回滚时间戳
                statement='update user set last_timestamp="%s", pushed=1 where id="%s"'%('0',username)
                res_=helper.commit(statement)
                logger.debug('[完成任务]重置用户时间戳为0,返回值为'+str(res_))
                ret['message']='任务超时，不予处理'
                self.reply(ret);return
            if wangwang==None:
                # 查询旺旺
                statement='select wangwang from user where id="%s"'%(username)
                wangwang=helper.query(statement)[0][0]
            # 提醒卖家后台审核
            statement='update user_order set status="1",order_id="%s",wangwang="%s" where id="%s" and username="%s"'%(order_id,wangwang,user_order_id,username)
            print(statement)
            res=helper.commit(statement)
            ret['code']=res
        elif code=='10':
            '''
            卖家查询订单
            op=0:查询页数，op=1：查询信息
            '''
            self.user_order_heartbeat_all()
            op=int(self.get_argument('op',1))
            # 根据任务id筛选
            mission_id=self.get_argument('mission_id',None)
            if mission_id!=None:
                mission_id_statement=' mission_id="%s" and '%(mission_id)
            else:
                mission_id_statement=''
            # 根据店铺筛选
            shop=self.get_argument('shop',None)
            if shop!=None:
                shop_statement=' shop="'+shop+'" and '
            else:
                shop_statement=''
            # 任务时间筛选
            begin_time=self.get_argument('begin_time',None)
            end_time=self.get_argument('end_time',None)
            if begin_time!=None and end_time!=None:
                begin_time=str(self.date2stamp(begin_time))
                end_time=str(self.date2stamp(end_time))
                time_statement=' accept_time>"'+begin_time+'" and accept_time<"'+end_time+'" and '
            else:
                time_statement=''
            # 根据商品名筛选
            good_name=self.get_argument('good_name',None)
            if good_name!=None:
                good_name_statement=' good_name="'+good_name+'" and '
            else:
                good_name_statement=''
            # 根据状态筛选
            status=self.get_argument('status',None)
            if status!=None:
                status_statement=' status="'+status+'" and '
            else:
                status_statement=''
            num_per_page=int(num_per_page)
            page=int(self.get_argument('page',0))
            statement='select count(*) from user_order where'+mission_id_statement+shop_statement+time_statement+good_name_statement+status_statement+' seller_username="%s"'%(seller_username)
            ret['count']=helper.query(statement)
            ret['page_num']=int(num_per_page)
            helper=DBHelper(1)
            statement='select * from user_order where'+shop_statement+mission_id_statement+time_statement+good_name_statement+status_statement+' seller_username="%s" order by cast(accept_time as decimal) desc limit %d,%d'\
                %(seller_username,page*num_per_page,num_per_page)
            print(statement)
            res=helper.query(statement)
            ret['data']=[]
            for row in res:
                cur_username=row['username']
                wangwang=''
                if cur_username!=None and cur_username!='':
                    statement='select wangwang from user where id='+cur_username
                    res_=helper.query(statement)
                    if len(res_)>0:
                        wangwang=res_[0]['wangwang']
                row['wangwang']=wangwang
                accept_time=row['accept_time']
                if accept_time==None:
                    accept_time=0
                row['accept_time']=self.decode_stamp(accept_time)
                row['finish_time']=self.decode_stamp(row['finish_time'])
                raw_status=row['status']
                row['status']=self.decode_order_status(row['status'])
                time_left=user_timeout-time.time()+float(accept_time)
                if time_left<0:
                    time_left=0
                row['time_left']=time_left
                '''
                if time_left==0:
                    statement='update user_order set status=4 where id='+str(row['id'])
                    res_=helper.commit(statement)
                    if res_!=0:
                        #print(statement)
                        pass
                    else:
                        status=4
                    row['status']=self.decode_order_status(4)
                    if raw_status==0:
                        helper.commit('update user set last_timestamp=0 where id='+row['username'])
                '''
                row['user_order_id']=row['id']
                row['order_begin_time']=self.decode_stamp(row['order_begin_time'])
                row['begin_time']=self.decode_stamp(row['begin_time'])
                row['end_time']=self.decode_stamp(row['end_time'])
            ret['code']=0
            ret['data']=res
            #print(res)
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
                    ' from user_order where seller_username="%s" and status="2" and finish_time>"%s" and finish_time<"%s" order by cast(finish_time as decimal)'\
                    %(seller_username,begin_date,end_date)
            res=helper.query(statement)
            ret['data']=[]
            mission_money=0
            good_money=0
            order_num=0
            master_money=0
            slave_money=0
            for row in res:
                d_row=dict()
                d_row['master_money']=row[0]
                d_row['slave_money']=row[1]
                d_row['good_price']=row[2]
                d_row['finish_time']=row[3]
                d_row['mission_money']=row[0]+row[1]
                mission_money+=row[0]+row[1]
                good_money+=row[2]
                order_num+=1
                master_money+=row[0]
                slave_money+=row[1]
                ret['data'].append(d_row)
            ret['code']=0
            ret['mission_money']=mission_money
            ret['good_money']=good_money
            ret['order_num']=order_num 
            ret['master_money']=master_money
            ret['slave_money']=slave_money
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
                        ' from user_order where seller_username="%s" and username="%s" order by  cast(accept_time as decimal) desc limit %d,%d'\
                        %(seller_username,username,page*num_per_page,num_per_page)
                else:
                    statement='select mission_id,username,accept_time,finish_time,success,status,order_id,reason '+\
                        ',wangwang,keyword,good_name,begin_time,end_time,master_money,slave_money'+\
                        ' from user_order where seller_username="%s" and username="%s" and status="%s" order by '+\
                        ' cast(accept_time as decimal) desc limit %d,%d'\
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
            username=self.get_username()
            helper=DBHelper(1)
            statement='select * from cash_order where username="%s" order by id desc '%(username)
            res=helper.query(statement)
            if res!=None and len(res)>0:
                ret['code']=0
                ret['data']=res
                for row in ret['data']:
                    row.pop('create_date')
            else:
                ret['message']='没有明细'
        elif code=='14':
            '''
            根据任务获取订单id
            '''
            mission_id=self.get_argument('mission_id')
            helper=DBHelper(1)
            statement='select * from user_order where mission_id='+mission_id 
            ret['code']=0
            ret['data']=helper.query(statement)
        elif code=='15':
            '''
            用户注册
            '''
            wechat_id=self.get_argument('wechat_id','')
            # whether use already exist
            statement='select id,role from user where wechat_id="%s"'%(wechat_id)
            res=helper.query(statement)
            if res!=None and len(res)>0:
                ret['message']='用户已存在'
                self.reply(ret);return
            master_id=self.get_argument('inviter_id','0')
            master_wechat_id='0'
            if master_id!='0':
                # Query master wechat_id
                statement='select wechat_id from user where id="%s" and role=4'%(master_id)
                res=helper.query(statement)
                if res==None or len(res)==0:
                    ret['message']='邀请人ID不存在'
                    self.reply(ret);return
                master_wechat_id=helper.query(statement)[0][0]
            age=self.get_argument('age')
            gender=self.get_argument('gender')
            wangwang=self.get_argument('wangwang')
            extra=self.get_argument('extra','')
            phone=self.get_argument('phone')
            intent_role=self.get_argument('intent_role')
            images=''
            role=0
            for key in self.request.files:
                file_metas=self.request.files[key]
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
                    images+=new_file_name+' '
            images=images.strip()
            '''
            if 'comment_image' in self.request.files and 'my_taobao_image' in self.request.files:
                comment_image=''
                my_taobao_image=''
                file_metas=self.request.files['comment_image']
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
                    comment_image=new_file_name
                file_metas=self.request.files['my_taobao_image']
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
                    my_taobao_image=new_file_name
                '''
            statement='insert into user (wechat_id,inviter_id,age,gender,wangwang,'+\
                'images,role,seller_username,create_date,master_id,master_wechat_id,extra,phone,last_timestamp,intent_role) values '+\
                '("%s","%s","%s","%s","%s","%s","0","%s",now(),"%s","%s","%s","%s",%f,"%s")'\
                %(wechat_id,master_id,age,gender,wangwang,images,seller_username,
                        master_id,master_wechat_id,extra,phone,0,intent_role)
            res=helper.commit(statement)
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
            statement='select shop from shops where seller_username="%s"'%(seller_username)
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
                statement='insert into shops (seller_username,shop) values ("%s","%s")'\
                        %(seller_username,shop_name)
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
                pass
                '''
                shop_name=self.get_argument('shop_name')
                mission_interval=self.get_argument('mission_interval')
                statement='update shops set mission_interval="%s" where seller_username="%s" and shop="%s"'\
                        %(mission_interval,seller_username,shop_name)
                #print(statement)
                ret['code']=helper.commit(statement)
                '''
            else:
                pass
        elif code=='17':
            '''
            用户提现
            '''
            # TODO-B: 当数额较大时增加安全校验
            # 查询提现时间
            username=self.get_username()
            op=self.get_argument('op')
            # op=0: 查询余额，op=1:提现
            statement='select good_money,mission_money from cash_order where username="%s" order by id desc'%(username)
            good_money,mission_money=0,0
            res=helper.query(statement)
            if res!=None:
                for row in res:
                    good_money+=row[0]
                    mission_money+=row[1]
            # Query user account
            statement='select id,cash_op,cash_left,detail,create_date '+\
                    'from cash_order where username="%s" order by id desc limit 1'\
                    %(username)
            res=helper.query(statement)
            if len(res)>0 and res[0][0]!=None:
                cash_id,cash_op,cash_left,detail,create_date=res[0]
                cash_left=float(cash_left)
                if op=='0':
                    ret['cash_left']=cash_left
                    ret['good_money']=good_money
                    ret['mission_money']=mission_money
                    ret['code']=0
                    print('查询余额:',ret)
                elif op=='1':
                    statement='select setting from seller where username="%s"'%(seller_username)
                    setting=helper.query(statement)
                    if setting!=None and len(setting)>0 and setting[0][0]!=None and setting[0][0]!='':
                        cash_begin_hour,cash_begin_minute=0,0
                        cash_end_hour,cash_end_minute=24,60
                        setting=json.loads(setting[0][0])
                        cash_begin_hour,cash_begin_minute=setting['cash_begin_time'].split(':')
                        cash_end_hour,cash_end_minute=setting['cash_end_time'].split(':')
                    else:
                        cash_begin_hour,cash_begin_minute=9,0
                        cash_end_hour,cash_end_minute=17,0
                    now=datetime.datetime.now()
                    cur_hour,cur_minute=now.hour,now.minute
                    if cur_hour<int(cash_begin_hour) or cur_hour>int(cash_end_hour):
                        ret['message']='不在允许提现的时间段内'
                        self.reply(ret);return
                    if (cur_hour==int(cash_begin_hour) and cur_minute<int(cash_begin_minute)) or \
                            (cur_hour==int(cash_end_hour) and cur_minute>int(cash_end_minute)):
                        self.reply();return
                    money=float(self.get_argument('money'))
                    if money>=1 and cash_left>money:
                        #将数据写入数据库，提交提现
                        cash_op=-money
                        detail='正常提现'
                        cash_left=cash_left-money
                        cash_callback=self.pay_cash(money)
                        redpack_sn=''
                        extra=dict()
                        extra=json.dumps(extra)
                        ret=json.loads(cash_callback)
                        print('提现返回：',ret)
                        if ret['code']==0:
                            statement='insert into cash_order (username,cash_op,cash_left,detail,create_date,extra) values ("%s","%.4f","%.4f","%s",now(),\'%s\')'\
                                    %(username,cash_op,cash_left,detail,extra)
                            res=helper.commit(statement)
                else:
                    ret['message']='余额不足'
        elif code=='18':
            '''
            查询用户状态
            '''
            username=self.get_username()
            if username==None:
                ret['code']=2
                ret['message']='用户未注册'
            else:
                # 查询用户审核信息
                statement='select role from user where id="%s"'%(username)
                res=helper.query(statement)
                role=int(res[0][0])
                if role<3:
                    ret['code']=1
                    ret['id']=username
                    ret['message']=self.decode_role(role)
                else:
                    ret['code']=0
                    ret['master']=role==4
                    ret['id']=username
                    ret['message']='审核成功'
        elif code=='19':
            '''
            卖家确认订单
            op=0:通过订单，op=1:拒绝订单
            '''
            op=int(self.get_argument('op',0))
            order_id=self.get_argument('user_order_id')
            username=helper.query('select username from user_order where id="%s"'%(order_id))[0][0]
            openid=helper.query('select wechat_id from user where id='+username)[0][0]
            if op==0:
                # Step 1. 更改订单状态
                statement='update user_order set status="2",finish_time="%f" where id="%s"'%(time.time(),order_id)
                res=helper.commit(statement)
                print('更改订单状态成功',res)
                push_check_success(openid,datetime.datetime.now().strftime('%Y%m%d-%H%M'))
                # Step 2. 查询用户身份
                statement='select role,master_id,master_wechat_id from user where id="%s"'%(username) 
                res=helper.query(statement)
                role=int(res[0][0])
                master_id=res[0][1]
                master_wechat=res[0][2]
                # 查询订单状态
                statement='select mission_id from user_order where id="%s"'%(order_id)
                mission_id=helper.query(statement)[0][0]
                statement='select good_price,master_money,slave_money from user_order where id="%s"'%(order_id)
                good_price,master_money,slave_money=helper.query(statement)[0]
                assert slave_money!=0
                if role<3:
                    self.reply(ret);return;
                # Step 3. 查询用户现金账户并生成现金交易订单
                if role==3:
                    # 徒弟账户
                    statement='select id,cash_op,cash_left,detail,create_date,good_money,mission_money '+\
                        'from cash_order where username="%s" order by id desc limit 1'\
                        %(username)
                    res=helper.query(statement)
                    if res==None or len(res)==0 or res[0]==None:
                        slave_cash_left=0
                        slave_good_money=0
                        slave_mission_money=0
                    else:
                        slave_cash_left=float(res[0][2])
                        slave_good_money=float(res[0][5])
                        slave_mission_money=float(res[0][6])
                    slave_cash_op=good_price+slave_money
                    slave_cash_left+=good_price+slave_money
                    slave_good_money+=good_price
                    slave_mission_money+=slave_money
                    statement='insert into cash_order (username,cash_op,cash_left,detail,create_date,complete_user,good_money,mission_money)'+\
                        'values("%s","%f","%f","自己（徒弟）完成任务",now(),"%s","%f","%f")'\
                        %(username,slave_cash_op,slave_cash_left,username,slave_good_money,slave_mission_money)
                    res=helper.commit(statement)
                    print('更改徒弟现金订单',res)
                    # 师傅账户
                    statement='select id,cash_op,cash_left,detail,create_date,good_money,mission_money '+\
                        'from cash_order where username="%s" order by id desc limit 1'\
                        %(master_id)
                    res=helper.query(statement)
                    if res==None or len(res)==0 or res[0]==None:
                        master_cash_left=0
                        master_good_money=0
                        master_mission_money=0
                    else:
                        master_cash_left=float(res[0][2])
                        master_good_money=float(res[0][5])
                        master_mission_money=float(res[0][6])
                        # 通知师傅
                        master_wechat_id=helper.query('select wechat_id from user where id='+str(master_id))[0][0]
                        push_getmoney_fromstudent(master_wechat_id,master_good_money+master_mission_money,datetime.datetime.now().strftime('%Y%m%d-%H%M'))
                    master_mission_money+=master_money
                    master_cash_op=master_money
                    master_cash_left+=master_cash_op
                    statement='insert into cash_order (username,cash_op,cash_left,detail,create_date,complete_user,good_money,mission_money)'+\
                        'values("%s","%f","%f","徒弟完成任务",now(),"%s","%f","%f")'\
                        %(master_id,master_cash_op,master_cash_left,username,master_good_money,master_mission_money)
                    res=helper.commit(statement)
                    print('更改师傅现金订单',res)
                elif role==4:
                    # 师傅账户
                    statement='select id,cash_op,cash_left,detail,create_date,good_money,mission_money '+\
                        'from cash_order where username="%s" order by id desc limit 1'\
                        %(username)
                    res=helper.query(statement)
                    if res==None or len(res)==0:
                        master_cash_left=0
                        master_good_money=0
                        master_mission_money=0
                    else:
                        master_cash_left=float(res[0][2])
                        master_good_money=float(res[0][5])
                        master_mission_money=float(res[0][6])
                    master_cash_op=good_price+slave_money
                    master_cash_left+=master_cash_op
                    master_good_money+=good_price
                    master_mission_money+=slave_money
                    statement='insert into cash_order (username,cash_op,cash_left,detail,create_date,complete_user,good_money,mission_money)'+\
                        'values("%s","%f","%f","自己（师傅）完成任务",now(),"%s","%f","%f")'\
                        %(username,master_cash_op,master_cash_left,username,master_good_money,master_mission_money)
                    res=helper.commit(statement)
                    print('更改师傅现金订单',res)
                ret['code']=res 
            elif op==1:
                # Step 1. 更改订单状态
                statement='update user_order set status="3" where id="%s"'%(order_id)
                res=helper.commit(statement)
                push_check_fail(openid,datetime.datetime.now().strftime('%Y%m%d-%H%M'))
                ret['code']=res
        elif code=='20':
            '''
            卖家审核新手身份
            0审核中，1卖家审核完毕，2师傅审核完毕，3徒弟，4师傅
            '''
            username=self.get_username()
            # Query current user status
            statement='select role from user where id="%s"'%(username)
            status=int(helper.query(statement)[0][0])
            if status==0:
                status=1
            elif status==2:
                status=3
            else:
                self.reply(ret);return
            statement='update user set role="%d" where id="%s"'%(status,username)
            ret['code']=helper.commit(statement)
            if status==3:
                # 注册成功，通知用户
                open_id=self.get_argument('wechat_id')
                usr_id=username
                sign_time=datetime.datetime.now().strftime('%Y%m%d-%H%M')
                push_register_success(open_id,usr_id,sign_time)
        elif code=='21':
            '''
            师傅审核新手身份
            '''
            #TODO: 增加安全校验
            username=self.get_username()
            new_person_id=self.get_argument('new_person_id')
            # Query current user status
            statement='select role from user where id ="%s"'%(new_person_id)
            status=int(helper.query(statement)[0][0])
            if status==0:
                status=2
            elif status==1:
                status=3
            else:
                self.reply(ret);return
            statement='update user set role="%d" where id="%s"'%(status,new_person_id)
            ret['code']=helper.commit(statement)
            if status==3:
                # 注册成功，通知用户
                open_id=self.get_argument('wechat_id')
                usr_id=username
                sign_time=datetime.datetime.now().strftime('%Y%m%d-%H%M')
                push_register_success(open_id,usr_id,sign_time)
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
            print('卖家用户管理',self.request.body)
            statement='select count(*) from user where seller_username="%s" and role>=0'%(seller_username)
            ret['count']=helper.query(statement)
            ret['page_num']=num_per_page
            new_person=int(self.get_argument('new_person',0))
            master=self.get_argument('master',None)
            extra=self.get_argument('extra',None)
            if master==None or master=='1':
                master_statement=' role=4 and '
            else:
                master_statement=' role=3 and '
            if new_person==1:
                master_statement=' (role=0 or role=2) and '
            if extra!=None:
                extra_statement=r' extra like "%'+extra+r'%" and '
            else:
                extra_statement=''
            page=int(self.get_argument('page',0))
            helper=DBHelper(1)
            statement='select * from user where'+master_statement+extra_statement+' seller_username="%s"  order by create_date desc limit %d,%d '%(seller_username,page*num_per_page,num_per_page)
            print(statement)
            res=helper.query(statement)
            ret['code']=0
            if res==None:
                res=[]
            ret['data']=res
            for row in res:
                row['create_date']=row['create_date'].strftime("%Y%m%d-%H%M")
                row['role']=self.decode_role(row['role'])
                row['blacklist']=self.decode_blacklist(row['blacklist'])
                print(row)
        elif code=='25':
            '''
            师傅用户管理，查询用户
            '''
            master_id=self.get_username()
            helper=DBHelper(1)
            statement='select * from user where master_id="%s" and role>=0 order by create_date desc '%(master_id)
            res=helper.query(statement)
            ret['code']=0
            if res==None:
                res=[]
            ret['data']=res
            for row in res:
                row['create_date']=row['create_date'].strftime("%Y%m%d-%H%M")
                row['role']=self.decode_role(row['role'])
                row['blacklist']=self.decode_blacklist(row['blacklist'])
        elif code=='26':
            '''
            将徒弟升级到师傅
            '''
            username=self.get_username()
            statement='update user set role="4" where id="%s"'%(username)
            ret['code']=helper.commit(statement)
            # 发送通知
            openid=self.get_argument('wechat_id')
            push_upgrade(openid)
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
            statement='update seller set setting=\'%s\' where username="%s"'%(data,seller_username)
            ret['code']=helper.commit(statement)
        elif code=='32':
            '''
            查询提现时间段
            '''
            statement='select setting from seller where username="%s"'%(seller_username)
            setting=helper.query(statement)[0][0]
            if setting==None or setting=='':
                begin_time='09:00'
                end_time='17:00'
            else:
                data=json.loads(setting)
                begin_time=data['cash_begin_time']
                end_time=data['cash_end_time']
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
        elif code=='35':
            '''
            获取用户任务列表
            '''
            print('用户任务列表',self.request.body)
            username=self.get_username()
            # Sift is used to select order status, -1 for all
            sift=self.get_argument('sift',-1)
            if int(sift)==-1:
                statement='select id, mission_id,username,accept_time,finish_time,status,order_id,reason '+\
                    ',wangwang,keyword,good_name,begin_time,end_time,master_money,slave_money,shop,good_price'+\
                    ' from user_order where seller_username="%s"  and username="%s" order by cast(accept_time as decimal) desc'\
                    %(seller_username,username)
            else:
                statement='select id,mission_id,username,accept_time,finish_time,status,order_id,reason '+\
                    ',wangwang,keyword,good_name,begin_time,end_time,master_money,slave_money,shop,good_price'+\
                    ' from user_order where seller_username="%s" and status="%s" and username="%s" order by cast(accept_time as decimal) desc'\
                    %(seller_username,str(sift),username)
            res=helper.query(statement)
            print('任务列表',statement)
            ret['data']=[]
            for row in res:
                user_order_id,mission_id,username,accept_time,finish_time,status,order_id,reason,\
                    wangwang,keyword,good_name,begin_time,end_time,master_money,slave_money,shop,good_price=row
                row_dict=dict()
                row_dict['mission_id']=mission_id
                row_dict['username']=username
                row_dict['accept_time']=self.decode_stamp(accept_time)
                row_dict['finish_time']=self.decode_stamp(finish_time)
                row_dict['status']=status
                row_dict['order_id']=order_id
                row_dict['reason']=reason
                row_dict['wangwang']=wangwang
                row_dict['keyword']=keyword
                row_dict['good_name']=good_name
                row_dict['begin_time']=self.decode_stamp(begin_time)
                row_dict['end_time']=self.decode_stamp(end_time)
                row_dict['master_money']=master_money
                row_dict['slave_money']=slave_money
                row_dict['shop']=shop
                row_dict['good_price']=good_price
                row_dict['id']=user_order_id
                if accept_time==None:
                    accept_time=0
                time_left=user_timeout-time.time()+float(accept_time)
                if time_left<0:
                    time_left=0
                row_dict['time_left']=time_left
                if time_left==0 and status==0:
                    row_dict['status']=4
                    helper.commit('update user_order set status=4 where id='+str(user_order_id))
                    cur_timestamp=time.time()-7*3600*24
                    #statement='update mission set last_timestamp="%s" where id="%s"'%(str(cur_timestamp),mission_id)
                    #res_=helper.commit(statement)
                    statement='update user set last_timestamp="%s" where id="%s"'%('0',username)
                    res_=helper.commit(statement)
                    logger.debug('[获取用户列表]重置用户时间戳为0,返回值为'+str(res_))
                ret['data'].append(row_dict)
            ret['code']=0
        elif code=='36':
            '''
            获取徒弟贡献
            '''
            username=self.get_username()
            statement='select complete_user,cash_op from cash_order where username="%s" and complete_user!="%s"'\
                    %(username,username)
            ret['code']=0
            res=helper.query(statement)
            if len(res)>0:
                ret['data']=res
        elif code=='37':
            '''
            一键升级为师傅
            '''
            username=self.get_username()
            statement='update user set role=4 where id="%s"'%(username)
            open_id=self.get_argument('wechat_id')
            # 发送通知
            openid=self.get_argument('wechat_id')
            push_upgrade(openid)
            '''
            usr_id=username
            sign_time=datetime.datetime.now().strftime('%Y%m%d-%H%M')
            push_register_success(open_id,usr_id,sign_time)
            '''
            ret['code']=helper.commit(statement)
        elif code=='38':
            '''
            导出为excel
            '''
            shop=self.get_argument('shop',None)
            if shop!=None:
                shop_statement=' shop="'+shop+'" and '
            else:
                shop_statement=''
            # Sift is used to select order status, -1 for all
            user_order_ids=self.get_argument('user_order_ids')
            name=str(int(time.time()*100))+'.csv'
            path='/home/ubuntu/taobao/file/'+name
            with open(path,'wb') as f:
                f.write('订单ID,任务编号,用户ID,接单时间,完成时间,状态,淘宝订单号,旺旺号,关键词,商品名,师傅佣金,徒弟佣金,店铺名,商品价格,任务开始时间\n'.encode('GBK'))
                f.flush()
                for user_order_id in user_order_ids.split():
                    statement='select id,mission_id,username,accept_time,finish_time,status,order_id '+\
                            ',wangwang,keyword,good_name,begin_time,end_time,master_money,slave_money,shop,good_price'+\
                            ' from user_order where id="%s"'%(user_order_id)
                    res=helper.query(statement)
                    if len(res)==0:
                        continue
                    user_order_id,mission_id,username,accept_time,finish_time,status,order_id,\
                        wangwang,keyword,good_name,begin_time,end_time,master_money,slave_money,shop,good_price=res[0]
                    if order_id==None:
                        order_id=''
                    statement='select begin_time from mission where id="%s"'%(mission_id)
                    res=helper.query(statement)
                    if len(res)==0:
                        begin_time='未知'
                    else:
                        begin_time=self.decode_stamp(res[0][0])
                    sb=''
                    sb+=str(user_order_id)+','
                    sb+=str(mission_id)+','
                    sb+=str(username)+','
                    sb+=str(self.decode_stamp(accept_time))+','
                    sb+=str(self.decode_stamp(finish_time))+','
                    sb+=self.decode_order_status(status)+','
                    sb+=order_id+','
                    if wangwang==None:
                        if username!=None and username!=0:
                            statement='select wangwang from user where id='+username
                            wangwang=helper.query(statement)[0][0]
                        else:
                            wangwang=''
                    sb+=wangwang+','
                    sb+=keyword+','
                    sb+=good_name+','
                    sb+=str(master_money)+','
                    sb+=str(slave_money)+','
                    sb+=shop+','
                    sb+=str(good_price)+','
                    sb+=begin_time+'\n'
                    f.write(sb.encode('GBK'))
                    f.flush()
            ret['code']=0
            ret['url']='/file/'+name
        elif code=='39':
            '''
            查询是否有任务，如果没有，返回任务预期出现时间
            输入wechat_id，返回一个code和message，只需要打印出message就行了
            警告：逻辑发生改变，此时会返回可用任务列表
            '''
            # 用户通知心跳
            self.mission_available_heartbeat()
            # 刷新订单状态心跳
            self.user_order_heartbeat_all()
            # 获取参数
            self.secure_gate()
            username=self.get_username()
            wechat_id=self.get_argument('wechat_id')
            ret['data']=dict()
            # Query active mission
            statement='select id from user_order where username="%s" and status=0'%(username)
            res=helper.query(statement)
            if len(res)>0:
                ret['message']='请在任务管理中完成已有的任务'
                self.reply(ret);return
            # Query user's identity
            statement='select role,blacklist,mission_interval,last_timestamp from user where wechat_id="%s"'%(wechat_id)
            res=helper.query(statement)
            if len(res)>0:
                role,black_list,mission_interval,last_timestamp=res[0]
                if (black_list!=None and black_list!=0) or role==None or role==0:
                    ret['message']='您无法做任务'
                    self.reply(ret);return
            else:
                print(statement)
                ret['message']='您还未注册'
                self.reply(ret);return
            user_interval=res[0][2]
            if user_interval==None:
                user_interval=7
            user_last_timestamp=res[0][3]
            cur_timestamp=time.time()
            print(cur_timestamp,user_last_timestamp,user_interval)
            if cur_timestamp-user_last_timestamp<user_interval*24*3600:
                ret['message']='每%d天只能做一次任务'%(user_interval)
                self.reply(ret);return
            # Query active 
            statement='select * from mission '+\
                    'where seller_username="%s" and status="0" '%(seller_username)
            helper=DBHelper(1)
            res=helper.query(statement)
            # 预期等待
            cur_timestamp=time.time()
            missions=[]
            for row in res:
                '''
                if cur_timestamp-row['last_timestamp']>mission_heartbeat_interval:
                    helper.commit('update mission set last_timestamp=%f where id=%d'%\
                            (time.time(),row['id']))
                    self.user_order_heartbeat(row['id'])
                '''
            # 获取可用任务
            statement='select * from user_order where status=-1'
            res=helper.query(statement)
            if len(res)>0:
                # 返回获取任务成功
                ret['code']=0
                ret['message']='系统内有可接任务，点击申请任务可接取'
            else:
                statement='select * from mission where status=0 and seller_username="'+seller_username+'"'
                res=helper.query(statement)
                if len(res)==0:
                    ret['code']=3
                    ret['message']='暂时没有任务'
                    self.reply(ret);return
                waiting_time=3600*24*7
                now=time.time()
                for row in res:
                    mission_nums=row['mission_nums'].split()
                    total_nums=0
                    for m in mission_nums:
                        total_nums+=int(m)
                    begin_time=row['begin_time']
                    end_time=row['end_time']
                    interval=(end_time-begin_time)/total_nums
                    interval_count=int((now-begin_time)/interval)+1
                    remain=interval_count*interval+begin_time-now
                    if remain<waiting_time:
                        waiting_time=remain
                ret['waiting_time']=waiting_time
                ret['code']=1
            print(ret)
        elif code=='40':
            '''
            发送验证码
            '''
            phone=self.get_argument('phone').strip()
            if not phone.isdigit():
                ret['message']='手机号必须为数字'
                self.reply(ret);return
            verify_code=random.randint(100000,999999)
            statement='delete from phone_code where phone='+phone
            helper.commit(statement)
            statement='insert into phone_code (phone,verify_code) values("%s","%d")'%(phone,verify_code)
            res=helper.commit(statement)
            res=send_sms_code(int(phone),verify_code)
            ret['code']=res
            if res!=0:
                ret['message']='发送验证码失败'
            ret['verify_code']=verify_code
        elif code=='41':
            '''
            匹配验证码
            '''
            phone=self.get_argument('phone')
            verify_code=self.get_argument('verify_code')
            statement='select verify_code from phone_code where phone='+phone
            res=helper.query(statement)
            if len(res)>0:
                if int(res[0][0])==int(verify_code):
                    ret['code']=0
                    ret['message']='匹配成功'
                else:
                    ret['message']='验证码输入错误'
            else:
                ret['message']='验证码还未发送'
        elif code=='42':
            '''
            用户获取正在进行的任务
            '''
            username=self.get_username()
            wangwang=helper.query('select wangwang from user where id='+username)[0][0]
            helper=DBHelper(1)
            statement='select * from user_order where status=0 and username="%s"'%(username)
            res=helper.query(statement)
            if len(res)==0:
                # 判断是否有待审核的任务
                res=helper.query('select * from user_order where status=1 and username="%s" limit 1'%(username))
                if len(res)>0:
                    ret['code']=1
                    ret['message']='有未审核的任务'
                    ret['data']=res[0]
                    ret['data']['wangwang']=wangwang
                    self.reply(ret);return
                # 判断是否有审核通过的任务
                res=helper.query('select * from user_order where status=2 and username="%s" limit 1'%(username))
                if len(res)>0:
                    ret['code']=2
                    ret['message']='有审核通过的任务'
                    ret['data']=res[0]
                    ret['data']['wangwang']=wangwang
                    self.reply(ret);return
                # 判断是否有审核未通过的任务
                res=helper.query('select * from user_order where status=3 and username="%s" limit 1'%(username))
                if len(res)>0:
                    ret['code']=3
                    ret['message']='有审核未通过的任务'
                    ret['data']=res[0]
                    ret['data']['wangwang']=wangwang
                    self.reply(ret);return
                # 判断是否有超时的任务
                res=helper.query('select * from user_order where status=4 and username="%s" limit 1'%(username))
                if len(res)>0:
                    ret['code']=4
                    ret['message']='有超时的任务'
                    ret['data']=res[0]
                    ret['data']['wangwang']=wangwang
                    self.reply(ret);return
                ret['code']=5
                ret['message']='暂无正在进行的任务'
            else:
                if time.time()-float(res[0]['accept_time'])>user_timeout:
                    # 更新user_order
                    statement='update user_order set status=4 where status=0 and username="%s"'%(username)
                    helper.commit(statement)
                    # 更新user
                    statement='update user set last_timestamp=0 where id="%s"'%(username)
                    helper.commit(statement)
                    ret['code']=4
                    ret['message']='任务已超时'
                    ret['data']=res[0]
                    ret['data']['wangwang']=wangwang
                else:
                    ret['code']=0
                    ret['data']=res[0]
                    ret['data']['wangwang']=wangwang
        elif code=='43':
            '''
            获取用户基本信息
            '''
            username=self.get_username()
            helper=DBHelper(1)
            statement='select * from user where id="%s"'%(username)
            res=helper.query(statement)
            ret['code']=0
            ret['data']=res[0]
            ret['data'].pop('create_date')
        elif code=='44':
            '''
            用户获取任务列表
            '''
            username=self.get_username()
            wangwang=helper.query('select wangwang from user where id='+username)[0][0]
            helper=DBHelper(1)
            statement='select * from user_order where username="%s" order by accept_time desc'%(username)
            res=helper.query(statement)
            ret['code']=0
            for row in res:
                row['status']=self.decode_order_status(row['status'])
                row['wangwang']=wangwang
            ret['data']=res
        elif code=='45':
            '''
            卖家添加注释
            '''
            user_comment=self.get_argument('user_comment')
            statement='update seller set user_comment="%s" where username="%s"'%(user_comment,seller_username)
            res=helper.commit(statement)
            ret['code']=res
        elif code=='46':
            '''
            卖家获取注释
            '''
            ret['code']=0
            res=helper.query('select user_comment from seller where username="%s"'%(seller_username))[0][0]
            if res==None:
                res=''
            ret['data']=res
        elif code=='47':
            '''
            更改订单价格
            '''
            user_order_id=self.get_argument('user_order_id')
            good_price=self.get_argument('good_price')
            res=helper.commit('update user_order set good_price=%s where id="%s"'%(good_price,user_order_id))
            ret['code']=res
        elif code=='48':
            '''
            根据user_order_id查询任务详情
            '''
            user_order_id=self.get_argument('user_order_id')
            helper=DBHelper(1)
            statement='select * from user_order where id='+user_order_id
            res=helper.query(statement)
            if len(res)==0:
                ret['message']='没有此任务'
            else:
                ret['code']=0
                ret['data']=res[0]
                if 'create_date' in ret['data']:
                    ret['data'].pop('create_date')
                ret['data']['status']=self.decode_order_status(ret['data']['status'])
                ret['data']['accept_time']=self.decode_stamp(ret['data']['accept_time'])
                mission_id=res[0]['mission_id']
                statement='select * from mission where id='+str(mission_id)
                res_=helper.query(statement)
                for k in res_[0]:
                    if k not in ret['data'] and k!='create_date':
                        ret['data'][k]=res_[0][k]
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
            if shop not in shop_cache:
                # Query shop interval
                statement='select mission_interval from shops where seller_username="%s" and shop="%s"'\
                        %(seller_username,shop)
                res=helper.query(statement)
                if res==None or len(res)==0 or res[0][0]==None:
                    shop_interval=3
                else:
                    shop_interval=res[0][0]
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
        if x==None:
            return '00000000-0000'
        x=float(x)
        if x==0:
            return 0
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
            return str(res[0][0])
        else:
            return None

    def decode_order_status(self,x):
        if x==None:
            return '状态错误'
        x=int(x)
        if x==-2:
            return '执行中'
        elif x==-1:
            return '未接单'
        if x==0:
            return '已接单'
        elif x==1:
            return '待审核'
        elif x==2:
            return '已返现'
        elif x==3:
            return '审核失败'
        elif x==4:
            return '任务超时'
        elif x==5:
            return '已取消'
        elif x==6:
            return '未接单'
        else:
            return '参数错误'
    def pay_cash(self,money,open_id=None):
        '''
        Get user id and pay him.
        #返回值是一个dict，key“redpackurl”是红包链接
        '''
        if open_id==None:
            open_id=self.get_argument('wechat_id')
        money=int(money*100)
        now=datetime.datetime.now().strftime("%Y%m%d-%H%M")
        print('[INFO] Executing pay_cash',open_id,money)
        r=requests.post(pay_url_prefix,{'open_id':open_id,'money':money}).text
        print('提现请求返回:',r)
        push_cash_success(open_id,money/100,now)
        return r;

    def get_open_id(self,code,appid=None,secret=None):
        if appid==None or secret==None:
            helper=DBHelper()
            seller_username=self.get_argument('seller_username')
            statement='select appid,secret from seller where username="%s"'%(seller_username)
            appid,secret=helper.query(statement)[0]
        #apiurl="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="+appid+"&secret="+appsecret
        apiurl="https://api.weixin.qq.com/sns/oauth2/access_token?appid="+appid+"&secret="+secret+"&code="+code+"&grant_type=authorization_code"
        response= urllib.request.urlopen(apiurl).read().decode('utf-8')
        print('获取微信openid',response)
        j=json.loads(response)
        for key in j:
            if key == 'openid':
                return j['openid']
   
    def reply(self,ret):
        print(ret)
        self.set_header("Access-Control-Allow-Origin", "*") # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.write(json.dumps(ret))

    def checkredpack(self,redpack_sn):
        #查询红包，唯一参数 红包编号，redpack_sn
        method="jfy.redpacks.get"
        jsdict_2=OrderedDict();
        jsdict_2['appkey']=myappkey
        jsdict_2['method']=method
        jsdict_2['redpack_sn']=redpack_sn
        jsoncheck=json.dumps(jsdict_2)
        response= urllib.request.urlopen(apiurl,jsoncheck).read().decode('utf-8')
        temp=json.loads(response)
        return temp;
    def date2stamp(self,x):
        '''
        x: 20180501-0502
        '''
        x=x.replace('-','')
        assert len(x)==12,x
        Y,m,d,H,M=int(x[:4]),int(x[4:6]),int(x[6:8]),int(x[8:10]),int(x[10:])
        t=datetime.datetime(Y,m,d,H,M)
        return t.timestamp()
    def norm_user_stamp(self,stamp):
        '''
        将时间戳从凌晨开始计算
        @modify: 当前版本不需要正则化
        '''
        return stamp
        date_origin=datetime.datetime.fromtimestamp(float(stamp))
        new_date=datetime.datetime(date_origin.year,date_origin.month,date_origin.day,23,59)
        return new_date.timestamp()

    def user_order_heartbeat_all(self):
        '''
        更新全部的订单状态
        '''
        # 判断是否应该刷新订单状态
        with open('config/order_heartbeat') as f:
            last=float(f.read())
        now=time.time()
        if now-last<self.mission_heartbeat_interval:
            return
        with open('config/order_heartbeat','w') as f:
            f.write(str(now))
        helper=DBHelper(1)
        # 处理任务超时信息
        statement='update mission set status=2 where status=0 and end_time<'+str(time.time())
        helper.commit(statement)
        # 更改超时逻辑
        # 当用户任务下发一个小时后取消任务
        now=time.time()
        statement='update user_order set status=4 where %f-order_begin_time>"%d" and status=-1'%(now,3600)
        helper.commit(statement)
        statement='update user_order set status=-1 where status=-2 and  order_begin_time<'+str(time.time())
        helper.commit(statement)

    def user_order_heartbeat(self,mission_id):
        '''
        更新任务状态,下发任务
        '''
        helper=DBHelper(1)
        # 处理任务超时信息
        statement='update mission set status=2 where status=0 and end_time<'+str(time.time())
        helper.commit(statement)
        # 更改超时逻辑
        # 当用户任务下发一个小时后取消任务
        now=time.time()
        statement='update user_order set status=4 where %f-order_begin_time>"%d" and status=-1'%(now,3600)
        helper.commit(statement)
        statement='update user_order set status=-1 where status=-2 and mission_id='+str(mission_id)+' and order_begin_time<'+str(time.time())
        return helper.commit(statement)
    def mission_available_runner(self):
        '''
        执行用户推送刷新
        '''
        # 判断是否有可用任务
        helper=DBHelper(1)
        statement='select count(*) from mission where status=0'
        if helper.query(statement)==0:
            return
        now=time.time()
        statement='select id,wechat_id from user where (last_timestamp-%f)>3600*24*mission_interval and pushed=0'%(now)
        res=helper.query(statement)
        for row in res:
            openid=row['wechat_id']
            now=datetime.datetime.now().strftime('%Y%m%d-%H%M')
            push_cando_mission(openid,now)
        statement='update user set pushed=1 where last_timestamp-%f>3600*24*mission_interval and pushed=0'%(time.time())
        helper.commit(statement)
        
    def mission_available_heartbeat(self):
        '''
        周期性地判断用户是否可以刷新任务
        @Info: 刷新所有用户的信息
        @Info: 采用多进程
        '''
        # 判断是否应该刷新任务
        with open('config/push_heartbeat') as f:
            last=float(f.read())
        now=time.time()
        if now-last>self.push_heartbeat_interval:
            with open('config/push_heartbeat','w') as f:
                f.write(str(now))
            multiprocessing.Process(target=self.mission_available_runner).start()
