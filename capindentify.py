# !/usr/bin/env python3
# -*- coding: utf -8 -*-
import warnings

from PIL import Image
from skimage import data,filters, io, img_as_uint
from skimage.filters import threshold_otsu
from skimage.morphology import disk
import pytesseract


WHITE = 255
BLACK = 0

file = 'captcha.jpg'


class captchaindetify(object):
    '''
    验证码识别程序
    '''
    def __init__(self):

        self.threshold = 6
        self.table = []

    # 1.灰度化
    # 2.二值处理
    # 3.pytesseract识别
    def pre(self, file='captcha.jpg'):
        img = Image.open(file)
        # 1.灰度
        img = img.convert('L')
        # self.img.show()
        # 2.二值
        for i in range(256):
            if i < self.threshold:
                self.table.append(BLACK)
            else:
                self.table.append(WHITE)
        out = img.point(self.table, '1')
        out.save('grey'+file)
        # 降噪
        img = data.imread('grey'+file, as_grey=True)
        edges = filters.median(img, disk(2))
        io.imsave('grey'+file, edges)

        image = io.imread('grey'+file)
        thresh = threshold_otsu(image)
        binary = image > thresh
        io.imsave('grey'+file, img_as_uint(binary))

    def codeIndetify(self, file='temp.jpg'):
        file = 'grey'+file
        image = Image.open(file)
        # 识别不出来之后，有warn报错，这里捕获一下
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            try:
                vcode = pytesseract.image_to_string(image)
            except:
                vcode = ''
        return vcode


if __name__ == '__main__':
    app = captchaindetify()
    # app.pre(file)
    app.codeIndetify('temp.jpg')
