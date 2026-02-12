from pixiv_download import config
from pixiv_download import utils
from pixiv_download import download
from pathlib import Path
from concurrent import futures as cf
import sys
from datetime import datetime, timedelta



if __name__=="__main__":
    utils.if_ready()
    modes={"1":"daily","2":"daily_r18","3":"author","4":"tag","5":"default"}#5种模式
    mode=input(f"请选择模式:\n1:{modes['1']}\n2:{modes['2']}\n3:{modes['3']}\n4:{modes['4']}\n5:默认模式 获取当天排行榜前50的图片\n").strip()
    
    if mode not in modes.keys():
        print("[-]模式错误 请输入1-5")
        sys.exit(0)

    elif mode=="1" or mode=="2":#daily daily_r18
        date=input("请选择日期:\n例子:20260101\n").strip()
        utils.check_date(date)
        p=input("请选择页码:\n例子:1\n").strip()
        utils.check_p_page(p,modes[mode])
        path=str(config.path)+f"\\{date}_{modes[mode]}_{p}"
        path_other_name=str(config.path_other_name)+f"/{date}_{modes[mode]}_{p}"
        p1=Path(path_other_name)
        if_exist=p1.exists()
        if if_exist:
            if utils.if_file_exist(p1):
                print("[-]该日期已经获取到该模式的该页码的图片")
                print(f"[-]具体图片文件地址:{path}")
                sys.exit(0)
        else:
            p1.mkdir(parents=True,exist_ok=True)
            downloader=download.Base_downloader()
            url_mode_date=f"https://www.pixiv.net/ranking.php?mode={modes[mode]}&date={date}&format=json&p={p}"
            urls=downloader.to_daily_get_urls(url=url_mode_date)
            urls_set=[]
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor_1:
                for url in urls:
                    future=executor_1.submit(downloader.if_set_illsut,url)
                    futures.append(future)

                for future in futures:
                    try:
                        url=future.result()
                        if url!=False:
                            urls_set.append(url)
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor:
                for url in urls:
                    if url in urls_set:
                        future_a=executor.submit(downloader.download_a_set_image,url,path)     
                        futures.append(future_a)
                    else:
                        future_b=executor.submit(downloader.download_one_image,url,path)
                        futures.append(future_b)
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[-]下载图片失败:{e}",flush=True)
                        continue
            
    elif mode=="3":#作者模式
        date=datetime.now().date().strftime("%Y%m%d")
        uid=input("请输入作者id:\n例子:56970644\n").strip()
        p=input("请输入要获取的图片数量:\n例子:10\n").strip()
        utils.check_p(p)
        path=str(config.path)+f"\\{uid}_{date}_{p}"
        path_other_name=str(config.path_other_name)+f"/{uid}_{date}_{p}"
        p1=Path(path_other_name)
        if_exist=p1.exists()
        if if_exist:
            if utils.if_file_exist(p1):
                print(f"[-]该作者的前{p}张图片已经获取了")
                print(f"[-]具体图片文件地址:{path}")
                sys.exit(0)
        else:
            p1.mkdir(parents=True,exist_ok=True)
            downloader=download.Author_downloader()
            illusts_id=downloader.get_author_illusts_id(uid)
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor:#并发获取作者的作品url
                for i in range(0,(len(illusts_id) if int(p)>len(illusts_id) else int(p))):
                    future=executor.submit(downloader.get_author_illusts_url,uid,illusts_id[i])
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
                    future=executor_1.submit(downloader.if_set_illsut,url)
                    futures.append(future)

                for future in futures:
                    try:
                        url=future.result()
                        if url!=False:
                            urls_set.append(url)
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor:
                for url in urls:
                    if url in urls_set:
                        future_a=executor.submit(downloader.download_a_set_image,url,path)     
                        futures.append(future_a)
                    else:
                        future_b=executor.submit(downloader.download_one_image,url,path)
                        futures.append(future_b)
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[-]下载图片失败:{e}",flush=True)
                        continue

    elif mode=="4":#tag模式
        tag=input("请输入tag:\n例子:萝莉(loli)\n").strip()
        p=input("请输入页码:\n例子:1 (一页有50张图片)\n").strip()
        date=datetime.now().date().strftime("%Y%m%d")
        path=str(config.path)+f"\\{tag}_{date}_{p}"
        path_other_name=str(config.path_other_name)+f"/{tag}_{date}_{p}"
        p1=Path(path_other_name)
        if_exist=p1.exists()
        if if_exist:
            if utils.if_file_exist(p1):
                print(f"[-]该tag:{tag}的第{p}页图片已经获取了")
                print(f"[-]具体图片文件地址:{path}")
                sys.exit(0)
        else:
            p1.mkdir(parents=True,exist_ok=True)
            downloader=download.Tag_downloader()
            urls=downloader.to_tags_get_url(tag,p)
            urls_set=[]
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor_1:
                for url in urls:
                    future=executor_1.submit(downloader.if_set_illsut,url)
                    futures.append(future)

                for future in futures:
                    try:
                        url=future.result()
                        if url!=False:
                            urls_set.append(url)
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor:
                for url in urls:
                    if url in urls_set:
                        future_a=executor.submit(downloader.download_a_set_image,url,path)     
                        futures.append(future_a)
                    else:
                        future_b=executor.submit(downloader.download_one_image,url,path)
                        futures.append(future_b)
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[-]下载图片失败:{e}",flush=True)
                        continue
    elif mode=="5":#默认模式
        date=utils.return_yesterday()
        path=str(config.path)+f"\\每日榜单_{date}"
        path_other_name=str(config.path_other_name)+f"/每日榜单_{date}"
        p1=Path(path_other_name)
        if_exist=p1.exists()
        if if_exist:
            if utils.if_file_exist(p1):
                print("[-]今日已经获取到图片")
                print(f"[-]具体图片文件地址:{path}")
                sys.exit(0)
        else:
            p1.mkdir(parents=True,exist_ok=True)
            downloader=download.Base_downloader()
            urls=downloader.to_daily_get_urls(url="https://www.pixiv.net/ranking.php?mode=daily&format=json&p=1")
            urls_set=[]
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor_1:
                for url in urls:
                    future=executor_1.submit(downloader.if_set_illsut,url)
                    futures.append(future)

                for future in futures:
                    try:
                        url=future.result()
                        if url!=False:
                            urls_set.append(url)
                    except Exception as e:
                        print(f"[-]获取图片url失败:{e}",flush=True)
                        continue
            futures=[]
            with cf.ThreadPoolExecutor(max_workers=20) as executor:
                for url in urls:
                    if url in urls_set:
                        future_a=executor.submit(downloader.download_a_set_image,url,path)     
                        futures.append(future_a)
                    else:
                        future_b=executor.submit(downloader.download_one_image,url,path)
                        futures.append(future_b)
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[-]下载图片失败:{e}",flush=True)
                        continue





