import time
import os
import requests
import re
import uuid
import concurrent.futures as cf
import json
import sys
from datetime import datetime, timedelta
#代理设置
proxies={
        "https":"http://127.0.0.1:7890",
        'http': 'http://127.0.0.1:7890',
    }
#请求头设置
headers={
        "Referer":"https://www.pixiv.net/",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}
#cookies设置
cookies_dict = {

}
#图片保存路径
path_image="D:\\qb"

def if_ready():#检查代理是否开启
    url="https://www.pixiv.net/"
    with requests.get(url=url,proxies=proxies,headers=headers,cookies=cookies_dict) as res:
        if res.status_code!=200:
            print(f"[-]请求失败 状态码:{res.status_code} 代理未开启")
            sys.exit(0)
        else:
            print("[+]代理已开启")
            return True
def res_close(res):#关闭响应
    res.close()
    res.connection.close()

def mkdir(path_a):#创建文件夹
    if not os.path.exists(path_a):
        os.makedirs(path_a)
        return False#如果文件不存在就创建文件夹 返回False
    else:
        return True#存在则返回True

def get_author_illusts_id(uid):#获取作者的所有图片id
    url=f"https://www.pixiv.net/ajax/user/{uid}/profile/all"
    with requests.get(url=url,proxies=proxies,headers=headers,cookies=cookies_dict) as res:
        text=json.loads(res.text)
        if text["error"]==True:
            print(f"[-]输入的作者uid:{uid}不存在 请检查uid是否正确",flush=True)
            sys.exit(0)
        illusts_id=[int(key) for key in text["body"]["illusts"].keys()]
    return illusts_id

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
def to_url_get_illust_id(url):#通过url获取图片id
    illust_id=re.sub(pattern="_p0.*",repl="",string=url.split("/")[-1])
    return illust_id

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

def get_author_illusts_url(uid,illust_id,flag=0):#获取作者的指定插画id作品的url
    url_illust=f"https://www.pixiv.net/ajax/user/{uid}/illusts?ids%5B%5D={illust_id}&lang=zh"
    with requests.get(url=url_illust,proxies=proxies,headers=headers,cookies=cookies_dict) as res:
        data=json.loads(res.text)
        url=data["body"][f"{illust_id}"]["url"]
        print(f"[+]illust_id为{illust_id}的图片url已成功获取",flush=True)
        return fix_url(url,illust_id)

def download_a_set_image(url,path):#下载作品集
    illusts_id=to_url_get_illust_id(url)
    suffix=url.split(".")[-1]
    path=path+f"\\{illusts_id}_作品集"
    mkdir(path)
    url_page=f"https://www.pixiv.net/ajax/illust/{illusts_id}"
    try:
        with requests.get(url=url_page,proxies=proxies,headers=headers,cookies=cookies_dict) as res:
            data=json.loads(res.text)
            pageCount=data["body"]["pageCount"]#获取作品集中图片的数量
    except Exception as e:
        print(f"[-]错误信息:{e}")
        return False
    with cf.ThreadPoolExecutor(max_workers=20) as executor_download:
        for i in range(pageCount):
            url=re.sub(pattern=r'\d+\.'+re.escape(suffix),repl=f"{i}.{suffix}",string=url)
            executor_download.submit(download_one_image,url,path,flag=1)
        return True
            
def if_hot_image(id,max_retries=3):#检查图片是否热门
    url=f"https://www.pixiv.net/ajax/illust/{id}"
    for i in range(max_retries):
        try:
            with requests.get(url=url,proxies=proxies,headers=headers,cookies=cookies_dict) as res:
                text=json.loads(res.text)
                break
        except Exception as e:
            print(f"[-]错误信息:{e}")
            print(f"[-]正在进行第{i+1}次尝试")

    bookmarkCount=text["body"]["bookmarkCount"]
    if int(bookmarkCount)>=200:#如果收藏数大于等于200 则认为是热门图片
        return text["body"]["urls"]["original"]
    else:
        return False
    

def to_tags_get_url(tag,p=1):#通过tag获取图片url
    url=f"https://www.pixiv.net/ajax/search/artworks/{tag}?order=date_d&mode=safe&p={p}&csw=1&s_mode=s_tag&type=all&lang=zh"
    try:
        with requests.get(url=url,proxies=proxies,headers=headers,cookies=cookies_dict) as res:
            text=json.loads(res.text)
            total=text["body"]["illustManga"]["total"]
            last_page=text["body"]["illustManga"]["lastPage"]
            print(f"total:{total}")
            print(f"last_page:{last_page}")
            if int(p)>int(last_page) or int(p)<=0:
                print(f"[-]页码错误 页码不能小于等于0或大于{last_page}")
                print(f"[-]请检查你的页码是否正确:{p}")
                sys.exit(0)
            if total==0:
                print(f"[-]tag:{tag} 没有作品")
                sys.exit(0)
    except Exception as e:
        print(f"[-]错误信息:{e}")
        return False
    length=len(text["body"]["illustManga"]["data"])
    illusts_ids=[text["body"]["illustManga"]["data"][i]["id"] for i in range(length)]
    hot_images_urls=[]
    with cf.ThreadPoolExecutor(max_workers=20) as executor:
        futures=[]
        for i in range(length):
            future=executor.submit(if_hot_image,illusts_ids[i])
            futures.append(future)

        for future in futures:
            try:
                url=future.result()
                if url!=False:
                    hot_images_urls.append(url)
                    illusts_id=to_url_get_illust_id(url)
                    print(f"[+]成功爬取优质作品 作品id:{illusts_id}")
            except Exception as e:
                print("[-]错误信息:{e}")

    return hot_images_urls



def download_one_image(url,path,max_retries=3,flag=0):#下载单张图片
    illust_id=to_url_get_illust_id(url)
    for i in range(max_retries):
        try:
            res=requests.get(url=url,proxies=proxies,headers=headers,stream=True)#获取响应 流式传输 适合大文件下载
            status_code=res.status_code
            if status_code==404:#如果返回404 可能图片是.png格式
                res_close(res)
                url_1=re.sub(pattern=".jpg",repl=".png",string=url)
                res=requests.get(url=url_1,proxies=proxies,headers=headers,stream=True)
                status_code=res.status_code
                if res.status_code!=200:#如果不是200 则下载失败
                    if flag:
                        return False
                    print(f"[-]下载失败 作品id为:{illust_id} status_code:{status_code} 图片可能是gif格式",flush=True)
                    res_close(res)
                    return False
            name=uuid.uuid4().hex#生成随机文件名
            path_image_a=path+f"\\{name}.jpg"
            try:
                with open(path_image_a,"wb")as f:
                    for chunk in res.iter_content(chunk_size=8192):#在流式传输中 每次只读取8192字节
                        f.write(chunk)#每次写入8192字节
            except Exception as e:
                print(f"[-]下载失败 作品id为:{illust_id} 错误信息:{e}",flush=True)
                res_close(res)
                return False
            print(f"[+]illust_id为:{illust_id}的图片下载成功",flush=True)
            res_close(res)
            return True
            
        except Exception as e:
            print(f"[-]错误信息:{e}")
            num=i+1
            print(f"[-]正在尝试第{num}次重试")

def if_set_illsut(url):#检查图片是否是作品集
    suffix=url.split(".")[-1]
    status_code=None
    if suffix=="jpg":#可能是jpg 也可能是png 传进来的url并不能确定是哪一种
        repatern=r'\d+\.jpg'
        url_jpg=re.sub(pattern=repatern,repl="1.jpg",string=url)
        res=requests.get(url=url_jpg,proxies=proxies,headers=headers,cookies=cookies_dict)
        status_code=res.status_code
        if status_code==404:
            res_close(res)
            url_png_1=re.sub(pattern=".jpg",repl=".png",string=url_jpg)
            res=requests.get(url=url_png_1,proxies=proxies,headers=headers,cookies=cookies_dict)
            if res.status_code!=200:
                res_close(res)
                return False
            
    elif suffix=="png":
        repatern=r'\d+\.png'
        url_png=re.sub(pattern=repatern,repl="1.png",string=url)
        res=requests.get(url=url_png,proxies=proxies,headers=headers,cookies=cookies_dict)
        status_code=res.status_code
        if status_code==404:
            res_close(res)
            url_jpg_1=re.sub(pattern=".png",repl=".jpg",string=url_png)
            res=requests.get(url=url_jpg_1,proxies=proxies,headers=headers,cookies=cookies_dict)
            if res.status_code!=200:
                res_close(res)
                return False
    else:
        return False
    
    if res.status_code!=200:#最后通过status_code判断是否是作品集
        res_close(res)
        return False
    elif res.status_code==200:
        res_close(res)
        return url


def get_urls(url):#获取图片url
    #匹配url(该模式只匹配来自排行榜中的图片url)
    urls=[]
    with requests.get(url=url,proxies=proxies,headers=headers,cookies=cookies_dict) as res:
        text=json.loads(res.text)#获得网页源代码 先将其转换为json格式 再转换为字符串
        if "不正确的请求" in text:
            print("[-]url错误")
            print(f"[-]请检查你的url是否正确:{url}")
            sys.exit(0)
        length=len(text["contents"])
    for i in range(0,length):
        url=text["contents"][i]["url"]
        illust_id=text["contents"][i]["illust_id"]
        urls.append(fix_url(url,illust_id))
    return urls




if __name__=="__main__":
    if_ready()
    modes={"1":"daily","2":"daily_r18","3":"author","4":"tag","5":"default"}#3种模式
    mode=input(f"请选择模式:\n1:{modes['1']}\n2:{modes['2']}\n3:{modes['3']}\n4:{modes['4']}\n5:默认模式 获取当天排行榜前50的图片\n")
    if mode=="3":#作者模式
        uid=input("请输入作者id:\n例子:56970644\n")
        p=input("请输入要获取的图片数量:\n例子:10\n")
        check_p(p)
        illusts_id=get_author_illusts_id(uid)
        path=path_image+f"\\{uid}_{p}"
        if_exist=mkdir(path)
        file_size = os.path.getsize(path)
        if if_exist:
            if file_size!=0:
                print(f"[-]该作者的前{p}张图片已经获取了")
                print(f"[-]具体图片文件地址:{path}")
                sys.exit(0)
        else:
            with cf.ThreadPoolExecutor(max_workers=20) as executor:#并发获取作者的作品url
                futures=[]
                for i in range(0,(len(illusts_id) if int(p)>len(illusts_id) else int(p))):
                    future=executor.submit(get_author_illusts_url,uid,illusts_id[i])
                    futures.append(future)
                urls=[]
                for future in futures:
                    try:
                        urls.append(future.result())
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue
            urls_set=[]
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor_1:#并发检查图片是否是作品集
                for url in urls:
                    future=executor_1.submit(if_set_illsut,url)
                    futures.append(future)

                for future in futures:
                    try:
                        url=future.result()
                        if url!=False:
                            urls_set.append(url)
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue
            with cf.ThreadPoolExecutor(max_workers=20) as executor_download:#并发下载图片
                for url in urls:
                    if url in urls_set:
                        executor_download.submit(download_a_set_image,url,path)
                    else:
                        executor_download.submit(download_one_image,url,path)
    elif mode=="4":#tag模式
        tag=input("请输入tag:\n例子:萝莉(loli)\n")
        p=input("请输入页码:\n例子:1 (一页有50张图片)\n")
        path=path_image+f"\\{tag}_{p}"
        if_exist=mkdir(path)
        file_size = os.path.getsize(path)
        if if_exist:
            if file_size!=0:
                print(f"[-]该tag{tag}的第{p}页图片已经获取了")
                print(f"[-]具体图片文件地址:{path}")
                sys.exit(0)
        else:
            urls=to_tags_get_url(tag,p)
            urls_set=[]
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor_1:
                for url in urls:
                    future=executor_1.submit(if_set_illsut,url)
                    futures.append(future)

                for future in futures:
                    try:
                        url=future.result()
                        if url!=False:
                            urls_set.append(url)
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue

            with cf.ThreadPoolExecutor(max_workers=20) as executor:
                for url in urls:
                    if url in urls_set:
                        executor.submit(download_a_set_image,url,path)     
                    else:
                        executor.submit(download_one_image,url,path)


    elif mode=="5":#默认模式
        today=datetime.now().date()
        yesterday=today-timedelta(days=1)
        date=yesterday.strftime("%Y%m%d")
        path=path_image+f"\\每日榜单_{date}"
        if_exist=mkdir(path)
        file_size = os.path.getsize(path)
        if if_exist:
            if file_size!=0:
                print("[-]今日已经获取到图片")
                print(f"[-]具体图片文件地址:{path}")
                sys.exit(0)
        else:
            urls=get_urls(url="https://www.pixiv.net/ranking.php?mode=daily&format=json&p=1")
            urls_set=[]
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor_1:
                for url in urls:
                    future=executor_1.submit(if_set_illsut,url)
                    futures.append(future)

                for future in futures:
                    try:
                        url=future.result()
                        if url!=False:
                            urls_set.append(url)
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue

            with cf.ThreadPoolExecutor(max_workers=20) as executor:
                for url in urls:
                    if url in urls_set:
                        executor.submit(download_a_set_image,url,path)     
                    else:
                        executor.submit(download_one_image,url,path)

    elif mode not in ["1","2","3","4","5"]:
        print("[-]模式错误")
        sys.exit(0)

    else:#其他模式
        date=input("请选择日期:\n例子:20260101\n")
        check_date(date)
        p=input("请选择页码:\n例子:1\n")
        mode=modes[mode]
        check_p_page(p,mode)
        path=path_image+f"\\{date}_{mode}_{p}"
        if_exist=mkdir(path)
        file_size = os.path.getsize(path)
        if if_exist:
            if file_size!=0:
                print("[-]该日期已经获取到该模式的该页码的图片")
                print(f"[-]具体图片文件地址:{path}")
                sys.exit(0)
        else:
            url_mode_date=f"https://www.pixiv.net/ranking.php?mode={mode}&date={date}&format=json&p={p}"
            urls=get_urls(url=url_mode_date)
            urls_set=[]
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor_1:
                for url in urls:
                    future=executor_1.submit(if_set_illsut,url)
                    futures.append(future)

                for future in futures:
                    try:
                        url=future.result()
                        if url!=False:
                            urls_set.append(url)
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue

            with cf.ThreadPoolExecutor(max_workers=20) as executor:
                for url in urls:
                    if url in urls_set:
                        executor.submit(download_a_set_image,url,path)     
                    else:
                        executor.submit(download_one_image,url,path)
    

