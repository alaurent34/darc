#coding:utf-8
from time import time
START = time()
from datetime import datetime
##print ("処理開始：%s" % START.strftime("%H:%M:%S.")  + "%02d" % (START.microsecond // 1000))
##print  ("経過時間：%s 秒" % round( time() - START  ,2 ) )
#import numpy as np
#import pandas as pd
#from pandas import Series, DataFrame
#import pandas.tools.plotting as plotting
#pd.set_option('display.width', 400)  #数値を変更すると改行位置を変更できる
#import matplotlib.pyplot as plt
#import csv
#import random
#import statistics
#import hashlib
#import math
import os
##print ( os.system("tasklist | grep httpd") )
import re
import sys
from sys import argv
import io
###これが一番重いので開けるのは気をつける．エクセルを読み書きできるようになるよ．
###これ以外は，殆ど開けても使わなければ処理時間に大差無い
#import openpyxl

# 標準入出力の文字コードを明示的に指定
# apacheユーザで実行するとデフォルトでANSI_X3.4-1968になってしまうのため
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')



### 引数取得
ARGS = []
for i in range(len(argv)):
    ARGS.append(argv[i])
NUM_ARGS = len(ARGS)


### 標準入力を取得しDF型に変換




FILENAMES = []
BASE_M_FILENAME = ARGS[1].replace(  "Result_" , "M_"  )
FILENAMES.append( BASE_M_FILENAME  )                              ## M_test.csv
FILENAMES.append( BASE_M_FILENAME.replace(  "M_" , "T_"   )  )    ## T_test.csv
FILENAMES.append( BASE_M_FILENAME.replace(  "M_" , "AT_"   )  )   ## AT_test.csv
FILENAMES.append( BASE_M_FILENAME.replace(  "M_" , "P_"   )  )    ## P_test.csv


FILETYPE = []
FILETYPE.append('パーソナルデータ(属性)M');
FILETYPE.append('パーソナルデータ(履歴)T');
FILETYPE.append('パーソナルデータ(履歴)AT');
FILETYPE.append('行番号データP');


FILEOUTPUT = ""
LIMITS = len(FILENAMES) ## ファイルの数

#IN_FILENAME = str(JPATH) + str(CSVFILE)
#LINE_OUTPUT = open( IN_FILENAME , "r")
LIMIT = 0
FILES = 0
NUM   = 0
SPLIT = []

for i in sys.stdin:
    
    if NUM == LIMIT + 1:
            NUM = 0
    if NUM == 0 :
            before = time()
            #SPLIT = i.split(",")
            LIMIT = int(i)
    else:
            FILEOUTPUT = FILEOUTPUT + str(i) 
    if NUM == LIMIT:
            #print(FILEOUTPUT)
            FCSV = open(   (FILENAMES[FILES])  , 'w') # 上書きモードで
            FCSV.write( FILEOUTPUT )                               # ファイルに書き込む
            FCSV.close() 
            FILEOUTPUT = ""
            after = time()

            # 各項目ごとの行数と経過時間を出力
            print (FILETYPE[FILES] + ',' + FILENAMES[FILES] + ',' + str(LIMIT) + ',' + str(round( after - before , 3 )))
            FILES = FILES + 1
            
    NUM = NUM + 1
    

#print  ("経過時間：%s 秒" % round( time()-START  ,2 ) )
