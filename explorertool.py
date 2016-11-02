# !/usr/bin/env python3
# -- coding: utf-8 -*-
import gzip
import http
import random

import urllib.error
from enum import Enum, unique
from socket import timeout
import http.cookiejar
import urllib.request
import urllib.parse

import time

import shutil

import chardet
import math

import group
import regexp

USER_AGENTS_FILE = 'user_agents.txt'
CHARSET = 'utf-8'
COOKIE_FILE = 'cookie.txt'
_sentinel = object()
cj = None

@unique
class RAD(Enum):
    """
    NO就是浏览器头不随机
    ALL没调用一次，随机一个
    """
    NO = 0
    RANDOM = 1


def loaduseragents(uafile=USER_AGENTS_FILE, rad=RAD.NO):
    """
    uafile : string
            path to text file of user agents, one per line
    """

    head = {
        'Connection': 'Keep-Alive',
        'Cache-Control': 'max-age=0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }

    if rad != RAD.NO:
        uas = []
        with open(uafile, 'rb') as uaf:
            for ua in uaf.readlines():
                if ua:
                    # 对字符串欺骗，删除"符号
                    uas.append(ua.strip()[1:-1])
        choice = random.choice(uas).decode("utf-8")
        head['User-Agent'] = choice

    # print(head.get('User-Agent'))
    return head


def multi_open(url, data={}, urltimeout=2, charset='utf-8', retries=5, sleeptime=0):
    opener = makemyopener()
    while retries > 0:
        # 这里如果出现联网失败时候，可能出现重连的情况，这种情况下，如果encodedata和data重名，就会出现编码问题
        if data:
            encodedata = urllib.parse.urlencode(data).encode(charset)
            try:
                time.sleep(sleeptime)
                uop = opener.open(url, encodedata, urltimeout)
                return uop
            except (urllib.error.HTTPError, urllib.error.URLError, timeout) as error:
                retries -= 1
        else:
            try:
                time.sleep(sleeptime)
                uop = opener.open(fullurl=url, timeout=urltimeout)
                return uop
            except (urllib.error.HTTPError, urllib.error.URLError, timeout) as error:
                retries -= 1
    raise urllib.error.URLError(reason='连接失败', filename=url)


def uzipdata(data):
    """
    网页解压缩
    """
    # 解码
    chardit = chardet.detect(data)
    if chardit['encoding']:
        charset = chardit['encoding']
    else:
        charset = CHARSET
    try:
        html = gzip.decompress(data).decode(charset)
    except:
        html = data.decode(charset)
    return html


# user_agents = LoadUserAgents(uafile='user_agents.txt')


def downloadcaptcha(imgurl, groupitem=None):
    """
    下载captcha
    """
    try:
        imgdata= multi_open(imgurl)
        imgdata = imgdata.read()
    except TimeoutError as e:
        raise TimeoutError('Timeout... %s' % e)
    except urllib.error.URLError as e:
        raise urllib.error.URLError('HTTPerror: %s' % e)
    # 获取话题网址数字
    if groupitem is None:
        topicnumber = math.floor(time.time())
    else:
        topicnumber = str.split(groupitem.get_url(), '/')[-1:][0]

    filepath = 'tmp/captcha' + str(topicnumber) + '.jpg'

    with open(filepath, 'wb+') as file:
        file.write(imgdata)
    return filepath


def loadcookies(cookiesfile=COOKIE_FILE):
    global cj
    cj = http.cookiejar.MozillaCookieJar(cookiesfile)
    try:
        cj.load(cookiesfile, ignore_discard=True, ignore_expires=True)
    except http.cookiejar.LoadError as e:
        # pass
        raise http.cookiejar.LoadError('cookie.txt file does not look like a Netscape format cookies file')
    except FileNotFoundError as e:
        # pass
        raise FileNotFoundError('cookie.txt not find!')
    finally:
        return cj


def getck():
    cj = loadcookies()
    return cj._cookies.get('.douban.com').get('/').get('ck').value


# 包装浏览器头和cookie信息，尝试登陆

def makemyopener(proxies=None):
    head = loaduseragents(rad=RAD.NO)

    # proxies = {
    #     'http': '127.0.0.1：8087',
    #     'http': '119.90.62.104:8080',
    #     'http':'119.29.232.113:3128'
    #            }
    # opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.ProxyHandler(proxy))

    try:
        cj = loadcookies()
    except EnvironmentError as e:
        pass

    proxieshandler = None
    if proxies:
        proxieshandler = urllib.request.ProxyHandler(proxies)

    cookies = urllib.request.HTTPCookieProcessor(cj)

    if proxieshandler and cookies:
        opener = urllib.request.build_opener(cookies, proxieshandler)
    elif proxieshandler:
        opener = urllib.request.build_opener(proxieshandler)
    elif cookies:
        opener = urllib.request.build_opener(cookies)
    else:
        opener = urllib.request.build_opener()

    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header

    return opener

from config_default import data
def getconfig():
    return data


def getgroupqueue(queue, topics):
    for topic in topics:
        gro = group.Group('https://www.douban.com/group/topic/' + topic[0], topic[1], topic[2], '')
        queue.put(gro)
    queue.put(_sentinel)
    return queue

if __name__ == '__main__':
    # opener = makemyopener()
    # uop = opener.open('https://www.baidu.com', timeout=1)
    # loaduseragents()
    # loaduseragents()
    from config_default import data

    data = getconfig(data)
