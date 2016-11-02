#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import urllib.error

import re
import json

import explorertool
URL = 'http://www.tuling123.com/openapi/api'
CHARSET = 'utf-8'


def resptext(content):
    '''
    小黄鸡
    '''

    if content is None:
        content = '你好呀！'

    data = {
        # 图灵机器人的key
        'key': '019f7aced94f46efabac337b24b091bc',
        'info': content,
        'loc': 'shanghai',
        'userid': 'tulingTest' # 账号
    }

    try:
        data = urllib.parse.urlencode(data).encode(CHARSET)
        response = urllib.request.urlopen(URL, data).read().decode(CHARSET)
    except urllib.error.HTTPError as e:
        raise urllib.error.HTTPError('熊本熊登陆错误...')

    response = json.loads(response)

    return response['text']
