#!/bin/bash

import os
from operator import itemgetter
filelists = []
for file in os.listdir():
    base, ext = os.path.splitext(file)
    if ext == '.avi':
        filelists.append([file, os.path.getctime(file)])
filelists.sort(key=itemgetter(1), reverse=True)
MAX_CNT = 15
for i,file in enumerate(filelists):
    if i > MAX_CNT - 1:
        os.remove(file[0])

