import os

# Config
file_postfix=['css','xml','js','html']
#directory=[r'D:\virtual　Ｆ\AndroidStudioProjects\Maxwell\app\src\main\java\pureview\buaa\cn\maxwell']
directory=['/home/ubuntu/taobao/static']
non_empty_counter=0
non_comment_counter=0
counter=0

def run(dir):
    global counter,non_comment_counter,non_empty_counter
    comment=False
    for item in os.listdir(dir):
        if os.path.isfile(dir+'/'+item):
            if item.split('.')[-1] in file_postfix:
                with open(dir+'/'+item,encoding='utf8') as f:
                    for l in f:
                        l=l.strip()
                        counter+=1
                        if l.strip()!='':
                            non_empty_counter+=1
                        if l.endswith('*/'):
                            comment=False
                            continue
                        if comment:
                            continue
                        if l.startswith("/*"):
                            comment=True
                        if l.startswith('//'):
                            continue
                        if l=='':
                            continue
                        non_comment_counter+=1
        else:
            run(dir+'/'+item)


if __name__ == '__main__':
    for dir in directory:
        run(dir)
    print('counter',counter)
    print('non_empty_counter',non_empty_counter)
    print('non_comment_counter',non_comment_counter)

