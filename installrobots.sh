#!/bin/sh
# http://www.scipy.org/install.html#scientific-python-distributions
sudo pip3 install numpy
sudo pip3 install numpy --upgrade
sudo apt-get install python3-numpy python3-scipy python3-matplotlib -y
sudo pip3 install cython
sudo pip3 install pyparsing
sudo pip3 install scikit-image
sudo pip3 install openpyxl
sudo pip3 install pytesseract