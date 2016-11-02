#! /usr/bin/env python3
# -*- coding: utf-8 -*-


class Group(object):
    def __init__(self, url, title, number, responsetext, imagepath=None, captchaid=None):
        self.__title = title
        self.__number = number
        self.__url = url
        self.__responsetext = responsetext
        self.__imagepath = imagepath
        self.__captchaid = captchaid

    def get_title(self):
        return self.__title

    def get_number(self):
        return self.__number

    def get_url(self):
        return self.__url

    def get_responsetext(self):
        return self.__responsetext

    def get_imagepath(self):
        return self.__imagepath

    def get_captchaid(self):
        return self.__captchaid

    def set_title(self, title):
        self.__title = title

    def set_number(self, number):
        self.__number = number

    def set_url(self, url):
        self.__url = url

    def set_responsetext(self, responsetext):
        self.__responsetext = responsetext

    def set_imagepath(self, imagepath):
        self.__imagepath = imagepath

    def set_captchaid(self,captchaid):
        self.__captchaid = captchaid

