# -*- coding:utf-8 -*-
'''
@Description: 库函数
@Author: lamborghini1993
@Date: 2019-08-01 19:02:52
@UpdateDate: 2019-08-01 19:04:01
'''

import time


def Time2Str(ti=-1, timeformat="%Y-%m-%d %H:%M:%S"):
    if ti < 0:
        ltime = time.localtime()
    else:
        ltime = time.localtime(ti)
    strtime = time.strftime(timeformat, ltime)
    return strtime
