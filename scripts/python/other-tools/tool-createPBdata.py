# -*- coding: utf-8 -*- 
from time import time
START = time()
from datetime import datetime

import numpy
import pandas as pd
from pandas import Series, DataFrame
import pandas.tools.plotting as plotting
pd.set_option('display.width', 400)  #数値を変更すると改行位置を変更できる
#import matplotlib.pyplot as plt
#import csv
#import random
#import statistics
#import openpyxl
import re
import hashlib
import math
import sys
from sys import argv
import io
import os
import logging

###############
#  How to use
#  type AT_file.txt | python createPBdata.py S_file.txt P_file.txt
# (ex) type c:\wamp\www\login\pws2017\FILES\BASE\AT_600.txt_3_20170808170725 | C:\wamp\python\python.exe -B c:\wamp\www\AP\PWS\2017\python\createPBdata.py c:\wamp\www\login\pws2017\FILES\BASE\S_600.txt_3_20170808170725 c:\wamp\www\login\pws2017\FILES\BASE\P_600.txt_3_20170808170725
###############


###logディレクトリ作成　古いlogはrename
if(os.path.exists(os.path.dirname(__file__) + '/log') == False):
    os.makedirs(os.path.dirname(__file__) + '/log')
else:
    file_date = datetime.fromtimestamp((os.stat(os.path.dirname(__file__) + '/log/process_info.log')).st_mtime).strftime('%Y%m%d')
    today_date = datetime.now().strftime('%Y%m%d')
    if(file_date < today_date):
        #古いファイルはrename
        os.rename(os.path.dirname(__file__) + '/log/process_info.log' , os.path.dirname(__file__) + '/log/process_info_' + str(file_date) + '.log')


###logger設定
#rootロガーを取得
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#出力のフォーマットを定義
formatter = logging.Formatter('%(asctime)s - %(filename)s - pid:%(process)d - %(name)s - %(levelname)s - %(message)s')

#sys.stderrへ出力するハンドラーを定義
#sh = logging.StreamHandler(stream=sys.stdout)
#sh.setLevel(logging.INFO)
#sh.setFormatter(formatter)

#ファイルへ出力するハンドラーを定義
fh = logging.FileHandler(filename=os.path.dirname(__file__) + '/log/process_info.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

#rootロガーにハンドラーを登録する
#logger.addHandler(sh)
logger.addHandler(fh)



# 標準入出力の文字コードを明示的に指定
# apacheユーザで実行するとデフォルトでANSI_X3.4-1968になってしまうのため
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

###############
### 処理start
logger.info('-----------------------------')
logger.info('[start process]')


###############
### 引数取得
ARGS = []
for i in range(len(argv)):
    ARGS.append(argv[i])
NUM_ARGS = len(ARGS)
logger.info('[get args] ' + (' '.join(ARGS)))

### 出力ファイルpath取得
OUTPUT_FILE = []
for i in ARGS[1:NUM_ARGS]:
    OUTPUT_FILE.append(i)


###############
###  標準出力を読み込む
data = []
for line in sys.stdin:
    line = line.replace('\n','')
    data.append(line.split(','))
DATA = pd.DataFrame(data)
logger.info('[get stdin and convert to dataframe]')



##Noneの値を含む行を削除(行番号はそのまま保持される) 
DATA = DATA.dropna()
##DELを含まない行を抽出する(行番号はそのまま保持される) 
DATA = DATA[DATA[0] != 'DEL']
logger.info('[delete DEL lines]')

##日付型に変換
DATA[2] = pd.to_datetime(DATA[2])
DATA[2] = DATA[2].apply(lambda x: x.strftime('%Y/%m/%d'))

###日付とPsu.IDでsort
DATA = DATA.sort_values(by=[2,0], ascending=[True,True])
logger.info('[sort by date and psu.id]')

##日付の頭の0を取り除く(日付型に変換した際に頭に0をつけてしまう)
DATA[2] = DATA[2].str.replace('/0','/')

#print(DATA)
#print(DATA.index)
#print(list(DATA.index))

### T1を出力
DATA.to_csv(OUTPUT_FILE[0], sep=',', index=False, header=False)
logger.info('[output]' + str(OUTPUT_FILE[0]) )

### P(行番号)をDataFrame型にして出力
ROW = pd.DataFrame(DATA.index)
### 全ての値に+1
ROW = ROW + 1
#print(ROW)
ROW.to_csv(OUTPUT_FILE[1], sep=',', index=False, header=False)
logger.info('[output]' + str(OUTPUT_FILE[1]) )


print ("outputpath1:" + str(OUTPUT_FILE[0]) )
print ("outputpath2:" + str(OUTPUT_FILE[1]) )
print ("経過時間:%s 秒" % round( time() - START  ,2 ) )

#### 正常終了
logger.info('[process has succeeded]')
logger.info('[end process]')
