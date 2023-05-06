#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import threading
import time
from multiprocessing import Pool, cpu_count
import requests
from lxml import etree

#网站地址
CRAWL_URL = r'https://sj.zol.com.cn/bizhi/'
#图片存储的文件夹
SAVE_PATH = r'zol手机壁纸库'
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}
#下载页数
SIZE = 2

def clear(dir_path):
    """
    删除空文件夹

    :param dir_path: 文件夹路径
    """
    if os.path.exists(dir_path):
        #判断是否为文件夹
        if os.path.isdir(dir_path):
            #列出文件夹下面内容
            for d in os.listdir(dir_path):
                path = os.path.join(dir_path, d)
                if os.path.isdir(path):
                    # 递归删除空文件夹
                    clear(path)
        if not os.listdir(dir_path):
            os.rmdir(dir_path)
            print("remove the empty dir: {}".format(dir_path))


def save_images(src, name):
    """
    保存图片到本地

    :param src: 图片 src
    :param name: 保存图片名
    """
    try:
        img = requests.get(src, headers=HEADERS)
        with open(name + ".jpg", "ab") as f:
            f.write(img.content)
            print("{}.jpg save Successfully".format(name))
    except:
        pass

def mkdir(folder_name):
    """
       新建文件夹并切换到该目录下
       :param folder_name: 文件夹名称
    """
    path = os.path.join(SAVE_PATH, folder_name)
    if not os.path.exists(path=path):
        #创建文件
        os.makedirs(path)
        #切换到新建文件夹目录

        return path
    return False

def get_urls():
    """
       获取壁纸套图地址
       # 1080x1920(iphone6s plus)
       # 800x1280
       # 768x1280
       # 750x1334(iphone6)
       # 720x1280
       # 640x1336(iphone5/5s)
       """
    url = os.path.join(CRAWL_URL, "1080x1920/{}.html")
    _urls = set()
    for url in [url.format(page) for page in range(1, SIZE)]:
        res = requests.get(url=url, headers=HEADERS).text

        tree = etree.HTML(res)
        ul = tree.xpath('//ul[@class="pic-list2  martop clearfix"]/li[@class="photo-list-padding"]')
        for li in ul:
            pic_url = li.xpath('./a/@href')[0]
            _urls.add(pic_url)
        time.sleep(3)
    return _urls
#多线程锁lock。
lock = threading.Lock()

def run(url):
    '''
    启动
    :param url: 图片套图地址
    :return:
    '''
    url = 'https://sj.zol.com.cn' + url
    res = requests.get(url=url, headers=HEADERS).text
    tree = etree.HTML(res)
    #壁纸套图名，也作文件夹名
    title = tree.xpath('//div[@class="wrapper photo-tit clearfix"]/h1/a/text()')[0]
    #壁纸套图数量
    ul = tree.xpath('//*[@id="showImg"]/li')

    with lock:
        pic_path = mkdir(title)
        #避免重复添加数据
        if not pic_path:
            return
        for li in ul:
            pic_url = li.xpath('./a/img/@src')[0]
            save_images(pic_url, os.path.join(pic_path, pic_url[-12:-5]))


if __name__ == "__main__":

    urls = get_urls()
    #进程池
    pool = Pool(processes=cpu_count())
    try:
        #map() 放入迭代参数，返回多个结果
        #apply_async()只能放入一组参数，并返回一个结果，如果想得到map()的效果需要通过迭代
        pool.map(run, urls)
    except:
        time.sleep(30)
        pool.map(run, urls)
    clear(SAVE_PATH)
    print("程序完成快去查看下载的精美壁纸吧！！！")


