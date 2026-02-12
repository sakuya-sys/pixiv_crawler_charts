from pixiv_download import config
from pixiv_download import utils
from pixiv_download import download
from pathlib import Path
from concurrent import futures as cf
import sys
import argparse
from datetime import datetime, timedelta



def daily_or_daily_r18_downloader(mode,date,p=1):
    utils.check_date(date)
    utils.check_p_page(p,mode)
    path=str(config.path)+f"\\{date}_{mode}_{p}"
    path_other_name=str(config.path_other_name)+f"/{date}_{mode}_{p}"
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
        url_mode_date=f"https://www.pixiv.net/ranking.php?mode={mode}&date={date}&format=json&p={p}"
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
            
def author_downloader(uid,p):
    utils.check_p(p)
    date=datetime.now().date().strftime("%Y%m%d")
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

def tag_downloader(tag,p):
    date=datetime.now().date().strftime("%Y%m%d")
    path=str(config.path)+f"\\{tag}_{date}_{p}"
    path_other_name=str(config.path_other_name)+f"/{tag}_{date}_{p}"
    p1=Path(path_other_name)
    if_exist=p1.exists()
    if if_exist:
        if utils.if_file_exist(p1):
            print(f"[-]该tag{tag}的第{p}页图片已经获取了")
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
def default_downloader():
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




def cli():
    utils.if_ready()
    parser = argparse.ArgumentParser(description='Pixiv 爬虫工具')
    subparsers = parser.add_subparsers(dest='mode', help='下载模式')

    # 1. 日榜
    daily_parser = subparsers.add_parser('daily', help='获取日榜')
    daily_parser.add_argument('--date', required=True, help='日期 YYYYMMDD')
    daily_parser.add_argument('--page', default='1', help='页码')

    # 2. R18日榜
    daily_r18_parser = subparsers.add_parser('daily_r18', help='获取R18日榜')
    daily_r18_parser.add_argument('--date', required=True, help='日期 YYYYMMDD')
    daily_r18_parser.add_argument('--page', default='1', help='页码')

    # 3. 作者
    author_parser = subparsers.add_parser('author', help='下载作者作品')
    author_parser.add_argument('--uid', required=True, help='作者ID')
    author_parser.add_argument('--num', default='10', help='获取作品数量')

    # 4. 标签
    tag_parser = subparsers.add_parser('tag', help='按标签搜索')
    tag_parser.add_argument('--name', required=True, help='标签名')
    tag_parser.add_argument('--page', default='1', help='页码')

    # 5. 默认（昨天日榜）
    subparsers.add_parser('default', help='日榜前50')


    args = parser.parse_args()

    # 根据模式调用对应的下载函数
    if args.mode == 'daily':
        daily_or_daily_r18_downloader('daily', args.date, args.page)
    elif args.mode == 'daily-r18':
        daily_or_daily_r18_downloader('daily_r18', args.date, args.page)
    elif args.mode == 'author':
        author_downloader(args.uid, args.num)
    elif args.mode == 'tag':
        tag_downloader(args.name, args.page)
    elif args.mode == 'default':
        default_downloader()
    else:
        parser.print_help()