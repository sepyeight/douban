# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from group import Group


def checkcaptchaexist(data):
    '''
    获取并下载验证码
    '''
    # 这里要检验验证码的问题.....
    regex = r'<img id="captcha_image" src="(.+?)" alt="captcha"'
    imgurl = re.findall(re.compile(regex), data)
    if imgurl:
        return imgurl[0]
    else:
        return None


def checkloginstatus(data):
    '''
    查找整个页面，发现没有权限则返回false.
    '''
    re_code = '<li style=".*">([\u4e00-\u9fa5]{3,12})。</li>'
    re_index = '你没有权限访问这个页面'

    rg = re.compile(re_code)
    m = re.findall(rg, data)
    if m:
        return False
    else:
        return True


def searchcaptchaid(data):
    captcha = re.findall(r'<input type="hidden" name="captcha-id" value="(.+?)"/>', data)
    if captcha:
        return captcha[0]
    else:
        return None


def searchtitle(data):
    h1regexp = r"<h1>([^%&',;=?$\x22]+)</h1>"
    h1 = re.match(h1regexp, data)
    if h1:
        return h1.group(1)
    else:
        return '哈哈哈'


def findalltopics(data):
    # topicsregexp = r'topic/(\d+?)/.*?class="">([^%&\',;=?$\x22]+)</a></td>.*?<td nowrap="nowrap" class="">(.*?)</td>'
    topicsregexp = r'topic/(\d+?)/" title="([^%&\',;=?$\x22]+)" class="">.*?</a></td>.*?<td nowrap="nowrap" class="">(.*?)</td>'
    topics = re.findall(topicsregexp, data, re.DOTALL)

    return topics

def checktopicresponse(data):
    topicsregexp = r'class="clearfix comment-item" id="(\d+?)"'
    topics = re.findall(topicsregexp, data, re.DOTALL)
    return topics
