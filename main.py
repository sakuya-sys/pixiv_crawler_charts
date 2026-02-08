import time
import os
import requests
import re
import uuid
import concurrent.futures as cf
import json

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


def res_close(res):#关闭响应
    res.close()
    res.connection.close()

def mkdir(path):#创建文件夹
    if not os.path.exists(path):
        os.makedirs(path)
        return False#如果文件不存在就创建文件夹 返回False
    else:
        return True#存在则返回True

def download_one_image(url,path):#下载单张图片
    try:
        res=requests.get(url=url,proxies=proxies,headers=headers,stream=True)#获取响应 流式传输 适合大文件下载
        status_code=res.status_code
        if status_code==404:#如果返回404 可能图片是.png格式
            res_close(res)
            url=re.sub(pattern=".jpg",repl=".png",string=url)
            res=requests.get(url=url,proxies=proxies,headers=headers,stream=True)
            if res.status_code!=200:#如果不是200 则下载失败
                print("[-]下载失败")
                res_close(res)
                return 0
        name=uuid.uuid4().hex#生成随机文件名
        path_image=path+f"\\{name}.jpg"
        with open(path_image,"wb")as f:
            for chunk in res.iter_content(chunk_size=8192):#在流式传输中 每次只读取8192字节
                f.write(chunk)#每次写入8192字节
        print("[+]图片下载成功")
        f.close()
        res_close(res)
        #time.sleep(2)
    except requests.exceptions.HTTPError as e:
        print(e)


def get_urls(url):#获取图片url
    pattern=r'["\']url["\']\s*:\s*["\'](https?://i\.pximg\.net/c/\d+x\d+/img-master/img/\d{4}/\d{2}/\d{2}/\d{2}/\d{2}/\d{2}/\d+_p\d+[^\s"\'<>]*)["\']'
    #匹配url(该模式只匹配来自排行榜中的图片url)
    with requests.get(url=url,proxies=proxies,headers=headers,cookies=cookies_dict) as res:
        text=str(json.loads(res.text))#获得网页源代码 先将其转换为json格式 再转换为字符串
        if not re.findall(pattern,text):
            print("[-]url错误")
            print(f"[-]请检查你的url是否正确:{url}")
            exit(0)
    urls=[]
    matchs=re.findall(pattern,text)
    pattern1="c/480x960/img-master"
    repl1="img-original"
    pattern2="_master1200"
    for url in matchs:
        temp=re.sub(pattern=pattern1,repl=repl1,string=url)
        url=re.sub(pattern=pattern2,repl="",string=temp)
        urls.append(url)
    return urls
if __name__=="__main__":
    modes=["daily","daily_r18","1"]#3种模式
    mode=input("请选择模式:\ndaily\ndaily_r18\n1 (默认模式:获取当天排行榜前50的图片)\n")
    if mode=="1":#默认模式
        urls=get_urls(url="https://www.pixiv.net/ranking.php?mode=daily&format=json&p=1")
        date=time.strftime("%Y%m%d",time.localtime())
        path=path_image+f"\\{date}"
        if_exit=mkdir(path)
        if if_exit:
            print("[-]今日已经获取到图片")
            exit(0)
        else:
            with cf.ThreadPoolExecutor(max_workers=5) as executor:
                for url in urls:
                    executor.submit(download_one_image(url,path))
    elif mode not in modes:
        print("[-]模式错误")
        exit(0)
    else:#其他模式
        date=input("请选择日期:\n例子:20260101\n")
        p=input("请选择页码:\n例子:1\n")
        url_mode_date=f"https://www.pixiv.net/ranking.php?mode={mode}&date={date}&format=json&p={p}"
        urls=get_urls(url=url_mode_date)
        path=path_image+f"\\{date}_{mode}_{p}"
        if_exit=mkdir(path)
        if if_exit:
            print("[-]该日期已经获取到该模式的该页码的图片")
            exit(0)
        else:
            with cf.ThreadPoolExecutor(max_workers=5) as executor:
                for url in urls:
                    executor.submit(download_one_image(url,path))
    


