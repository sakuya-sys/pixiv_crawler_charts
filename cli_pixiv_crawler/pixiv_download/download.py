import requests
import os 
from pixiv_download import config
from pixiv_download import utils
import re
import uuid
import json
import sys
from concurrent import futures as cf
import time

class Base_downloader:
        def __init__(self):
                self.proxies=config.proxy
                self.headers=config.header
                self.cookies=config.cookies
                self.max_retries=config.max_retries
                self.max_workers=config.max_workers
        

        def download_one_image(self,url,path,max_retries=3,flag=0):#下载单张图片
            illust_id=self.to_url_get_illust_id(url)
            for i in range(max_retries):
                try:
                    res=requests.get(url=url,proxies=self.proxies,headers=self.headers,stream=True,timeout=10)#获取响应 流式传输 适合大文件下载
                    status_code=res.status_code
                    if status_code==404:#如果返回404 可能图片是.png格式
                        utils.res_close(res)
                        url_1=re.sub(pattern=".jpg",repl=".png",string=url)
                        res=requests.get(url=url_1,proxies=self.proxies,headers=self.headers,stream=True,timeout=10)
                        status_code=res.status_code
                        if res.status_code!=200:#如果不是200 则下载失败
                            if flag:
                                return False
                            print(f"[-]下载失败 作品id为:{illust_id} status_code:{status_code} 图片可能是gif格式",flush=True)
                            utils.res_close(res)
                            return False
                    name=uuid.uuid4().hex#生成随机文件名
                    path_image_a=path+f"\\{name}.jpg"
                    try:
                        with open(path_image_a,"wb")as f:
                            for chunk in res.iter_content(chunk_size=8192):#在流式传输中 每次只读取8192字节
                                f.write(chunk)#每次写入8192字节
                    except Exception as e:
                        print(f"[-]下载失败 作品id为:{illust_id} 错误信息:{e}",flush=True)
                        utils.res_close(res)
                        return False
                    print(f"[+]illust_id为:{illust_id}的图片下载成功",flush=True)
                    utils.res_close(res)
                    return True
                    
                except Exception as e:
                    print(f"[-]错误信息:{e}")
                    num=i+1
                    print(f"[-]正在尝试第{num}次重试")
                    time.sleep(0.5)
        
        def to_daily_get_urls(self,url):#获取图片url
            #匹配url(该模式只匹配来自排行榜中的图片url)
            urls=[]
            with requests.get(url=url,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10) as res:
                text=json.loads(res.text)#获得网页源代码 先将其转换为json格式 再转换为字符串
                if "不正确的请求" in text:
                    print("[-]url错误")
                    print(f"[-]请检查你的url是否正确:{url}")
                    sys.exit(0)
                length=len(text["contents"])
            for i in range(0,length):
                url=text["contents"][i]["url"]
                illust_id=text["contents"][i]["illust_id"]
                urls.append(utils.fix_url(url,illust_id))
            return urls
        
        def if_set_illsut(self,url):#检查图片是否是作品集
            suffix=url.split(".")[-1]
            status_code=None
            if suffix=="jpg":#可能是jpg 也可能是png 传进来的url并不能确定是哪一种
                repatern=r'\d+\.jpg'
                url_jpg=re.sub(pattern=repatern,repl="1.jpg",string=url)
                res=requests.get(url=url_jpg,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10)
                status_code=res.status_code
                if status_code==404:
                    utils.res_close(res)
                    url_png_1=re.sub(pattern=".jpg",repl=".png",string=url_jpg)
                    res=requests.get(url=url_png_1,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10)
                    if res.status_code!=200:
                        utils.res_close(res)
                        return False
                    
            elif suffix=="png":
                repatern=r'\d+\.png'
                url_png=re.sub(pattern=repatern,repl="1.png",string=url)
                res=requests.get(url=url_png,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10)
                status_code=res.status_code
                if status_code==404:
                    utils.res_close(res)
                    url_jpg_1=re.sub(pattern=".png",repl=".jpg",string=url_png)
                    res=requests.get(url=url_jpg_1,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10)
                    if res.status_code!=200:
                        utils.res_close(res)
                        return False
            else:
                return False
            
            if res.status_code!=200:#最后通过status_code判断是否是作品集
                utils.res_close(res)
                return False
            elif res.status_code==200:
                utils.res_close(res)
                return url
            
        def download_a_set_image(self,url,path):#下载作品集
            illusts_id=self.to_url_get_illust_id(url)
            suffix=url.split(".")[-1]
            path=path+f"\\{illusts_id}_作品集"
            utils.mkdir(path)
            url_page=f"https://www.pixiv.net/ajax/illust/{illusts_id}"
            try:
                with requests.get(url=url_page,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10) as res:
                    data=json.loads(res.text)
                    pageCount=data["body"]["pageCount"]#获取作品集中图片的数量
            except Exception as e:
                print(f"[-]错误信息:{e}")
                return False
            with cf.ThreadPoolExecutor(max_workers=20) as executor_download:
                for i in range(pageCount):
                    url=re.sub(pattern=r'\d+\.'+re.escape(suffix),repl=f"{i}.{suffix}",string=url)
                    executor_download.submit(self.download_one_image,url,path,flag=1)
                return True
        
        def to_url_get_illust_id(self,url):#通过url获取图片id
            illust_id=re.sub(pattern="_p0.*",repl="",string=url.split("/")[-1])
            return illust_id
        
class Author_downloader(Base_downloader):
    def __init__(self):
        super().__init__()
    
    def get_author_illusts_id(self,uid):#获取作者的所有图片id
        url=f"https://www.pixiv.net/ajax/user/{uid}/profile/all"
        with requests.get(url=url,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10) as res:
            text=json.loads(res.text)
            if text["error"]==True:
                print(f"[-]输入的作者uid:{uid}不存在 请检查uid是否正确",flush=True)
                sys.exit(1)
            try:
                illusts_id=[int(key) for key in text["body"]["illusts"].keys()]
            except KeyError:
                print(f"[-]输入的作者uid:{uid}不存在作品 请检查uid是否正确",flush=True)
                sys.exit(1)
        return illusts_id
    
    def get_author_illusts_url(self,uid,illust_id,flag=0):#获取作者的指定插画id作品的url
        url_illust=f"https://www.pixiv.net/ajax/user/{uid}/illusts?ids%5B%5D={illust_id}&lang=zh"
        with requests.get(url=url_illust,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10) as res:
            data=json.loads(res.text)
            url=data["body"][f"{illust_id}"]["url"]
            print(f"[+]illust_id为{illust_id}的图片url已成功获取",flush=True)
            return utils.fix_url(url,illust_id)
        
class Tag_downloader(Base_downloader):
    def __init__(self):
        super().__init__()

    def if_hot_image(self,id,max_retries=3):#检查图片是否热门
        url=f"https://www.pixiv.net/ajax/illust/{id}"
        for i in range(max_retries):
            try:
                with requests.get(url=url,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10) as res:
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


    def to_tags_get_url(self,tag,p=1):#通过tag获取图片url
        url=f"https://www.pixiv.net/ajax/search/artworks/{tag}?order=date_d&mode=safe&p={p}&csw=1&s_mode=s_tag&type=all&lang=zh"
        try:
            with requests.get(url=url,proxies=self.proxies,headers=self.headers,cookies=self.cookies,timeout=10) as res:
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
                future=executor.submit(self.if_hot_image,illusts_ids[i])
                futures.append(future)

            for future in futures:
                try:
                    url=future.result()
                    if url!=False:
                        hot_images_urls.append(url)
                        illusts_id=self.to_url_get_illust_id(url)
                        print(f"[+]成功爬取优质作品 作品id:{illusts_id}")
                except Exception as e:
                    print("[-]错误信息:{e}")

        return hot_images_urls
    