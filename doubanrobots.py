#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# 需要的组件：chardet, openpyxl,pillow,scikit-image，scipy,matplotlib,pytesseract
# http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-image非官方windows包支持
import logging.config
import logging
import queue
import random
import threading
import urllib.request
import urllib.error
import urllib.parse
# 1.我们要使用现有的cookie文件进行尝试登陆，登陆成功
# 登陆失败的话，使用账户密码登陆，获取cookie信息，刷新cookie
import asyncio

import bearrobot
import explorertool

import time

import group
import hrefwrite2file
import regexp
from capindentify import captchaindetify



class douban_robot:
    def __init__(self):
        logging.config.fileConfig('logconfig.ini')

        self.data = explorertool.getconfig()
        self.charset = 'utf-8'
        self.timeout = 1000

    # 登陆应该分为两部分，1.测试是否登陆，2.重新登陆
    def check_login(self, url='https://www.douban.com/doumail'):

        logging.debug('check the login status...')

        try:
            uop = explorertool.multi_open(url)
            data = explorertool.uzipdata(uop.read())
            return regexp.checkloginstatus(data)
        except urllib.error.URLError as e:
            logging.error(e.filename)
            logging.error(e.reason)

    def re_login(self, login_url='https://www.douban.com/login'):
        '''
        拿到页面，查找验证码，有，下载，识别，登陆，没有，直接登陆
        '''

        logging.debug('login...')
        try:
            uop = explorertool.multi_open(login_url)
        except urllib.error.URLError as e:
            logging.error(e.filename)
            logging.error(e.reason)
            raise urllib.error.HTTPError(code=e.code, msg='连接失败', hdrs=None, url=login_url, fp=None)
        html = explorertool.uzipdata(uop.read())
        with open('cache.html', 'wb+') as file:
            file.write(html.encode(self.charset))

        # 这里要检验验证码的问题.....
        captchaimgurl = regexp.checkcaptchaexist(html)
        if captchaimgurl:
            captchaid = regexp.searchcaptchaid(html)
            filepath = explorertool.downloadcaptcha(captchaimgurl)

            app = captchaindetify()
            app.pre(filepath)
            vcode = app.codeIndetify(filepath)
            # vcode = input('请输入验证码：')


            if captchaid:
                self.data['captcha-solution'] = vcode
                self.data['captcha-id'] = captchaid
                # self.data['user_login'] = '登陆'
        try:
            uop = explorertool.multi_open(login_url, self.data)
        except urllib.error.URLError as e:
            logging.error(e.filename)
            logging.error(e.reason)

        cj = explorertool.cj
        cj.save(ignore_discard=True, ignore_expires=True)  # 保存cookie到cookie.txt中

    def sofa(self, group_id):
        # 四部，拿到group，group添加responsetext，查看group是否被回复，回复group
        logging.debug('sofa .... ')
        topicsqueue = queue.Queue()
        checkqueue = queue.Queue()
        repliesqueue = queue.Queue()

        t0 = threading.Thread(target=self.gettopicsqueue, args=(topicsqueue, group_id), name='LoopThread0')
        t1 = threading.Thread(target=self.setresponsetext, args=(topicsqueue, checkqueue), name='LoopThread1')
        t2 = threading.Thread(target=self.checkreplycondition, args=(checkqueue, repliesqueue), name='LoopThread2')
        # t3 = threading.Thread(target=self.checkreplycondition, args=(checkqueue, repliesqueue), name='LoopThread3')
        t0.start()
        t1.start()
        t2.start()
        # t3.start()
        t0.join()
        t1.join()
        t2.join()
        # t3.join()

        self.responsetopic(repliesqueue)
        # self.setresponsetext(topicsqueue)
        # self.checkreplycondition(topicsqueue)
        # self.responsetopic(topicsqueue)

    def respvcode(self, item, postdata):

        captchaimgpath = item.get_imagepath()

        if captchaimgpath:
            app = captchaindetify()
            app.pre(captchaimgpath)
            vcode = app.codeIndetify(captchaimgpath)
            # vocode = input('请输入验证码：')

            captchaid = item.get_captchaid()
            if captchaid:
                postdata['captcha-solution'] = vcode
                postdata['captcha-id'] = captchaid

    def gettopicsqueue(self, group_queue, group_id):
        logging.info('gettopicsqueue....')
        group_url = "https://www.douban.com/group/" + group_id + "/discussion?start=0"
        html = None
        try:
            uop= explorertool.multi_open(group_url, sleeptime=random.random() * 4)
            html = explorertool.uzipdata(uop.read())
        except urllib.error.URLError as e:
            logging.error(e.filename)
            logging.error(e.reason)

        topics = regexp.findalltopics(html)
        return explorertool.getgroupqueue(group_queue, topics)

    def setresponsetext(self, topicsqueue, checkqueue):
        logging.info('setresponsetext....')
        while True:
            item = topicsqueue.get()
            if item is explorertool._sentinel:
                topicsqueue.put(item)
                break
            if item.get_number() is '':
                item.set_responsetext(bearrobot.resptext(item.get_title()))
                checkqueue.put(item)
        checkqueue.put(explorertool._sentinel)

    def checkreplycondition(self, checkqueue, repliesqueue):
        # 1.拿到html
        # 2.查看是否有回复
        # 3.查看是否有captcha
        logging.info('checkreplycondition....')
        while True:

            item = checkqueue.get()
            if item is explorertool._sentinel:
                checkqueue.put(item)
                break
            url = item.get_url()
            try:
                uop = explorertool.multi_open(url)
                html = explorertool.uzipdata(uop.read())
            except urllib.error.URLError as e:
                logging.error(e.filename)
                logging.error(e.reason)

            if html is None:
                break

            if regexp.checktopicresponse(html):
                pass
            else:
                captchaimgurl = regexp.checkcaptchaexist(html)
                if captchaimgurl:
                    captchaid = regexp.searchcaptchaid(html)
                    filepath = explorertool.downloadcaptcha(captchaimgurl, item)
                else:
                    filepath = ''
                    captchaid = ''
                item.set_imagepath(filepath)
                item.set_captchaid(captchaid)
                repliesqueue.put(item)
        repliesqueue.put(explorertool._sentinel)

    def responsetopic(self, repliesqueue):
        logging.info('responsetopic....')
        while True:
            item = repliesqueue.get()
            if item is explorertool._sentinel:
                repliesqueue.put(item)

                break

            if item.get_number() is '':
               # ck = 1adK & rv_comment = hhh & start = 0 & submit_btn = % E5 % 8A % A0 % E4 % B8 % 8A % E5 % 8E % BB
                msgdata = {"ck": explorertool.getck(),
                           "rv_comment": item.get_responsetext(),
                           "start": "0",
                           "submit_btn": "加上去"
                           }
                if item.get_imagepath() == '':
                    pass
                else:
                    self.respvcode(item, msgdata)

                # 有时候是网络原因，有时候你发的帖子被系统删掉了，所以我们要try--catch--pass掉
                try:
                    explorertool.multi_open(item.get_url() + '/add_comment', msgdata, sleeptime=0)
                    logging.info(item.get_url())
                except urllib.error.URLError as e:
                    pass


if __name__ == '__main__':
    # 你没有权限访问这个页面。
    app = douban_robot()

    loginStatu = app.check_login()
    if not loginStatu:
        app.re_login()
        while not app.check_login():
            app.re_login()

    logging.info('login successful...')
    while True:
        time.sleep(random.randint(0, 2))

        app.sofa('399184')
        app.sofa('haixiuzu')
        app.sofa('taotaopaoxiao')
        app.sofa('11512')
        app.sofa('asshole')

