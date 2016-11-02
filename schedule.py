# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-

import subprocess
import sched
import time


def restart():
    output = subprocess.check_output(
        'ps -aux | grep py', shell=True).decode('utf-8')
    if 'doubanrobots.py' not in output:
        subprocess.call(['python3', 'doubanrobots.py'])


def start():
    subprocess.call(['python3', 'doubanrobots.py'])

if __name__ == '__main__':
    start()
    scheduler = sched.scheduler(time.time, time.sleep)
    while True:
        scheduler.enter(30 * 60, 1, restart)
        scheduler.run()
