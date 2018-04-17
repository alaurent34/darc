#coding:utf-8
from time import time
START = time()
from datetime import datetime
###print ("処理開始：%s" % START.strftime("%H:%M:%S.")  + "%02d" % (START.microsecond // 1000))
###print  ("経過時間：%s 秒" % round( time() - START  ,2 ) )

from sys import argv
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
#import pandas.tools.plotting as plotting
#import matplotlib.pyplot as plt
#import csv
#import math
#import random
#import statistics
import re
#import openpyxl
#import hashlib
#import base64
import os
pd.set_option('display.width', 600)  #数値を変更すると改行位置を変更できる


##############################
#### Sample Program
####   by Hidenobu Oguri   2017/08/07 
####    
#### Outline explanation
####   Read "M","T","A(T)" files, and creates the correspondence table "Pseudonym ID Map", 
####   each of every month between real IDs and pseudonym IDs.
#### 
#### How to use (Sample output)
####   python kameimap_edit.py M.csv T.csv AT_**.csv (made by tool-kamei.py)
####     -> output "Fh.csv", please check "Fh" format.
##############################


# 引数の定義と格納
ARGS = []
for i in range(len(argv)):
	ARGS.append(argv[i])
NUM_ARGS = len(ARGS)

FILE1  = ARGS[1]
FILE2  = ARGS[2]
FILE3  = ARGS[3]
FILE4  = "Fh_%s.csv" % datetime.now().strftime("%H%M%S")

MASTER            = pd.read_csv(r"%s" % FILE1  , header=None)
TRANS_BASE        = pd.read_csv(r"%s" % FILE2  , header=None)
TRANS_MARK        = pd.read_csv(r"%s" % FILE3  , header=None)


## 分割は月単位でやる形にするよ
DIV_ZONE  =  []
for i in range(len(TRANS_BASE[2])):
	DIV_LINE = TRANS_BASE[2][i].split("/") 
	DIV_ZONE.append( int ( DIV_LINE[1] ) )



#### これで実現できると良いのだが... 
#### 元データID__月__仮名ID   を結合したデータを作成し，ユニークチェックする．
T_SIZECHECK =[]
for i in range( len(TRANS_BASE[0]) ):
	TT =  str (   str(TRANS_BASE[0][i]) + "__" + str(DIV_ZONE[i]) + "__" +  str(TRANS_MARK[0][i]) )
	T_SIZECHECK.append( TT )  



## TのIDと日付のユニーク化
def unique(seq):
    new_list = []
    new_list_add = new_list.append
    seen = set()
    seen_add = seen.add
    for item in seq:
        if item not in seen:
            seen_add(item)
            new_list_add(item)
    return new_list





UNIQUE_T = unique(T_SIZECHECK)
## 重複の無いID数を確認
#print( len( UNIQUE_T) )







#### ここからMAPつくり
Da0=[]
for i in range(len(MASTER[0])):
	Da0.append("DEL")

MASTER_ID         = pd.DataFrame( { "MASTER" : MASTER[0]     ,1:Da0 ,2:Da0 ,3:Da0 ,4:Da0 ,5:Da0 ,6:Da0 ,7:Da0 ,8:Da0 ,9:Da0 ,10:Da0 ,11:Da0 ,12:Da0    } )
TRANSA_ID         = pd.DataFrame( { "BASE"   : TRANS_BASE[0] , "PSEU": TRANS_MARK[0], "ZONE": DIV_ZONE }   )

for i in range( len(UNIQUE_T) ):
	UNIQ_SPLIT =  UNIQUE_T[i].split("__") 
	#print( str( str(  UNIQ_SPLIT[0]) + str(  UNIQ_SPLIT[1]) + str(  UNIQ_SPLIT[2]) )    )
	if str(UNIQ_SPLIT[2]) != "DEL" :
		MASTER_ID.loc[(  MASTER_ID.MASTER == int( UNIQ_SPLIT[0]) ) , int(UNIQ_SPLIT[1]) ] = str(UNIQ_SPLIT[2])


MASTER_ID.to_csv( FILE4 , sep=',', index=False, header=False, columns=['MASTER',12,1,2,3,4,5,6,7,8,9,10,11])

## 正常にファイル出力されていれば出力
if(os.path.getsize(FILE4) > 0):
    ##print(MASTER_ID)

    ##行列の数を確認
    YY,XX = MASTER_ID.shape
    print( " %s は %s 行 %s 列" % (FILE4,YY,XX) )
    print( "経過時間：%s 秒" % round( time()-START  ,2 ) )
    print( "処理終了：%s" % datetime.now().strftime("%H:%M:%S"))




