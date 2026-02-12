import requests
import sys
import os
from pixiv_download import config
from datetime import datetime, timedelta


def if_file_exist(path):#检查文件是否存在
    with os.scandir(path) as item:
        return any(item)
    
def if_ready():#检查代理是否开启
    url="https://www.pixiv.net/"
    try:
        with requests.get(url=url,proxies=config.proxy,headers=config.header,cookies=config.cookies) as res:
            if res.status_code!=200:
                print(f"[-]请求失败 状态码:{res.status_code} 代理未开启")
                sys.exit(0)
            else:
                print("[+]代理已开启")
                return True
    except requests.exceptions.RequestException as e:
        print(f"[-]代理未开启 请求异常: {e} ")
        sys.exit(0)

def res_close(res):#关闭响应
    res.close()
    res.connection.close()

def mkdir(path_a):#创建文件夹
    if not os.path.exists(path_a):
        os.makedirs(path_a)
        return False#如果文件不存在就创建文件夹 返回False
    else:
        return True#存在则返回True
    

def check_date(date):#检查日期是否正确
    try:
        datetime.strptime(date, '%Y%m%d')
    except ValueError:
        print("[-]日期错误 日期格式必须为YYYYMMDD")
        print(f"[-]请检查你的日期是否正确:{date}")
        sys.exit(0)

def check_p(p):#检查图片数量是否正确
    if int(p)<=0:
        print("[-]图片数量错误 图片数量不能小于等于0")
        print(f"[-]请检查你的图片数量是否正确:{p}")
        sys.exit(0)



def check_p_page(p,mode):#检查页码是否正确
    if mode=="daily_r18":
        if int(p)<=0 or int(p)>2:
            print("[-]页码错误 页码不能小于等于0或大于2")
            print(f"[-]请检查你的页码是否正确:{p}")
            sys.exit(0)
    elif int(p)<=0 or int(p)>10:
        print("[-]页码错误 页码不能小于等于0或大于10")
        print(f"[-]请检查你的页码是否正确:{p}")
        sys.exit(0)

def fix_url(url,illust_id):#修复url格式
    url=url.split("/")
    url[3]="img-original"
    del url[4:6]
    url[-1]=f"{illust_id}_p0.jpg"
    return "/".join(url)

def  return_yesterday():#返回昨天的日期
    today=datetime.now().date()
    yesterday=today-timedelta(days=1)
    date=yesterday.strftime("%Y%m%d")
    return date