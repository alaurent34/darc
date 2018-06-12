#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# count deleted rows
# Author: Hidenobu Oguri
# J(M, T, AT) -> Utility score


from time import time
#START = time()
from datetime import datetime

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import sys
from sys import argv
import io
import os

sys.stdin  = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SIZE0 = []
SIZE1 = []
SIZE2 = []
A = 0

M_SIZE = int(sys.stdin.readline().replace(('\r'or'\n'),'\r\n'))
for i in range(M_SIZE):
	#A = A+1
	item_string = (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()
	#item_list = item_string.split(",")
	#SIZE0.append(item_list)
#MASTER = pd.DataFrame(SIZE0)
#print (MASTER)

T_SIZE = int(sys.stdin.readline().replace(('\r'or'\n'),'\r\n'))
for ii in range(T_SIZE):
	#A = A+1
	item_string = (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()
	#item_list = item_string.split(",")
	#SIZE1.append(item_list)
#TRANSACTION = pd.DataFrame(SIZE1)
#print (TRANSACTION)


AT_SIZE = int(sys.stdin.readline().replace(('\r'or'\n'),'\r\n'))
#print (AT_SIZE)
for iii in range(AT_SIZE):
	item_string = (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()
	if 'DEL,' not in item_string :
		item_list = item_string.split(",")
		SIZE2.append(item_list)
ATRANSACTION = pd.DataFrame(SIZE2)
#print (ATRANSACTION)
#print ( len(ATRANSACTION[0]) )

SCORE = np.round( float( 1 - ( int(len(ATRANSACTION[0])) / int(T_SIZE) )) , 4  )
print ( "%s,nrow" % SCORE  )
#print ("経過時間:%s 秒" % round( time() - START  ,2 ) )
