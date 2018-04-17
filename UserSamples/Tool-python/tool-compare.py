#coding:utf-8
from time import time
START = time()
from datetime import datetime
###print ("処理開始：%s" % START.strftime("%H:%M:%S.")  + "%02d" % (START.microsecond // 1000))
###print  ("経過時間：%s 秒" % round( time() - START  ,2 ) )

import sys
from sys import argv
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import pandas.tools.plotting as plotting
import matplotlib.pyplot as plt
import csv
import math
import random
import statistics
import re
import openpyxl
import hashlib
import base64
pd.set_option('display.width', 600)  #数値を変更すると改行位置を変更できる


##############################
#### Sample Program
####   by Hidenobu Oguri   2017/08/07
####   edit by Akari Tachibana   2017/08/28
####
#### Outline explanation
####   Read "J1(R,P)","J2(R,P)"  files, and calculate the Match rate (= Re-Identify rate).
#### 
#### How to use
####   python compare.py FILE1 FILE2
##############################


# 引数の定義と格納
ARGS = []
for i in range(len(argv)):
	ARGS.append(argv[i])
NUM_ARGS = len(ARGS)

FILE1  = ARGS[1]
FILE2  = ARGS[2]

##### FILE1をMAPとPの部分に分ける
MASTER_DATA1 = []
MASTER_DATA2 = []
count = 0
ROW1 = 0
ROW2 = 0
for line in open( FILE1 , 'r'):
    itemList = line[:-1].split(',')
    if(count == 0):
        ROW1 = int(itemList[0])
    elif(count > 0 and count <= ROW1):
        MASTER_DATA1.append(itemList)
    elif(count == ROW1 + 1):
        ROW2 = int(itemList[0])
    elif(count > (ROW1 + 1) and count <= ((ROW1 + 1) + ROW2)):
        MASTER_DATA2.append(itemList)
    count = count + 1

MASTER_MAP = pd.DataFrame(MASTER_DATA1)
MASTER_ROW = pd.DataFrame(MASTER_DATA2)
#print(MASTER_MAP)
#print(MASTER_ROW)


##### FILE2をMAPとPの部分に分ける
INPUT_DATA1 = []
INPUT_DATA2 = []
count = 0
ROW1 = 0
ROW2 = 0
for line in open( FILE2 , 'r'):
    itemList = line[:-1].split(',')
    if(count == 0):
        ROW1 = int(itemList[0])
    elif(count > 0 and count <= ROW1):
        INPUT_DATA1.append(itemList)
    elif(count == ROW1 + 1):
        ROW2 = int(itemList[0])
    elif(count > (ROW1 + 1) and count <= ((ROW1 + 1) + ROW2)):
        INPUT_DATA2.append(itemList)
    count = count + 1

INPUT_MAP = pd.DataFrame(INPUT_DATA1)
INPUT_ROW = pd.DataFrame(INPUT_DATA2)
#print(INPUT_MAP)
#print(INPUT_ROW)
#sys.exit()


###### ファイルをそれぞれ分割したまででタイム
HALF_TIME = time()

#####################
##### MAPの比較 #####
#####################

## MASTERの母数算出
YY,XX = MASTER_MAP.shape # 500, 13
ALL_NUM = YY * (XX-1)

map_error = 0

## まず，INPUTデータとMASTERデータのID列が同じであるかを調査
if(len(INPUT_MAP) > 0):
    if(len(MASTER_MAP[0]) == len(INPUT_MAP[0])):
        for i in range(len(MASTER_MAP[0])):
            #### MAP同士のIDが異なる
            if MASTER_MAP[0][i] != INPUT_MAP[0][i]  :
                print ( "[MAP]Result,Time:0.0," + str(round( (HALF_TIME - START)  ,2 )))
                map_error = 1
                break
    else:
        #### MAP同士のIDの数が異なる
        map_error = 1

if(map_error == 0):
    ### エラー格納用配列
    err_string = []

    ## その後，INPUTデータとMASTERデータの各列の一致数を調査
    POINT = 0
    DEL_COUNT = 0
    NOT_DEL = 0
    for i in range(1,XX):
        for ii in range(len(MASTER_MAP[0])):
            ### 母数と当り数からDELの数を除くためDELをカウント
            if MASTER_MAP[i][ii] == "DEL" :
                DEL_COUNT = DEL_COUNT + 1

            ### 各値の一致数をカウント
            if MASTER_MAP[i][ii] == INPUT_MAP[i][ii]  :
                POINT = POINT + 1
                if MASTER_MAP[i][ii] != "DEL":
                    NOT_DEL = NOT_DEL + 1
            else :
                err_string.append( "Error : " + str(i) + "列" + str(ii + 1) + "行 " +  str(MASTER_MAP[i][ii]) + " -> " + str( INPUT_MAP[i][ii] ) ) 
    
    ### 母数と当り数からDELの数を削除
    ALL_NUM = ALL_NUM - DEL_COUNT
    POINT = POINT - DEL_COUNT
    ### POINTがマイナス値になる場合は0にする
    if POINT < 0:
        POINT = 0
    

    ###### MAP行列の数を確認
    #YY,XX = MASTER_MAP.shape
    #print( "データは %s 行 %s 列" % (YY,XX) )
    #print( "経過時間 : %s 秒" % round( (END_MAP_COMPARE - HALF_TIME) + (HALF_TIME - START)  ,2 ) )
    #print( "処理終了 : %s" % datetime.now().strftime("%H:%M:%S"))
    #print ( "Total : " + str(ALL_NUM))
    #print ( "Match : " + str(POINT) )


###### MAPの比較完了までのタイム
END_MAP_COMPARE = time()



#####################
##### ROWの比較 #####
#####################

## MASTERの母数算出
YY,XX = MASTER_ROW.shape
ALL_NUM2 = YY

row_error = 0

### エラー格納用配列
err_string2 = []

## INPUTデータとMASTERデータの各列の一致数を調査
POINT2 = 0
if(len(INPUT_ROW) > 0):
    if(len(MASTER_ROW[0]) == len(INPUT_ROW[0])):
        for hh in range(len(MASTER_ROW[0])):
                if MASTER_ROW[0][hh] == INPUT_ROW[0][hh]  :
                        POINT2 = POINT2 + 1
                else :
                        err_string2.append( "Error : " + str(hh + 1) + "行 " +  str(MASTER_ROW[0][hh]) + " -> " + str( INPUT_ROW[0][hh] ) ) 
    else:
        #### ROQ同士のIDの数が異なる
        row_error = 1

###### MAP行列の数を確認
#YY,XX = MASTER_ROW.shape
#print( "データは %s 行 %s 列" % (YY,XX) )
#print( "経過時間 : %s 秒" % round( (END_ROW_COMPARE - END_MAP_COMPARE) + (HALF_TIME - START)  ,2 ) )
#print( "処理終了 : %s" % datetime.now().strftime("%H:%M:%S"))
#print ( "Total : " + str(ALL_NUM2))
#print ( "Match : " + str(POINT2) )


###### ROWの比較完了までのタイム
END_ROW_COMPARE = time()


#####################
##### 結果 出力 #####
#####################

###### MAPの一致率結果と算出時間出力
if(map_error == 0):
    print ( "[MAP]Result,Time:" + str(round(float(POINT)/float(ALL_NUM), 2)) + "," + str(round( (END_MAP_COMPARE - HALF_TIME) + (HALF_TIME - START)  ,2 )))
else:
    print ( "[MAP]Result,Time:0.0," + str(round( (END_MAP_COMPARE - HALF_TIME) + (HALF_TIME - START)  ,2 )))

###### ROWの一致率結果と算出時間出力
if(row_error == 0):
    print ( "[ROW]Result,Time:" + str(round(float(POINT2)/float(ALL_NUM2), 2)) + "," + str(round( (END_ROW_COMPARE - END_MAP_COMPARE) + (HALF_TIME - START)  ,2 )))
else:
    print ( "[ROW]Result,Time:0.0," + str(round( (END_ROW_COMPARE - END_MAP_COMPARE) + (HALF_TIME - START)  ,2 )))

print("母数:" + str(ALL_NUM))
print("当り:" + str(POINT))
print("DEL数:" + str(DEL_COUNT))
print("DELでなく当り:" + str(NOT_DEL))

#print(ALL_NUM2)
#print(POINT2)

###### MAPの一致していない結果を出力
#for n in range(len(err_string)):
#        print ("[MAP_ERROR]" + str(err_string[n]))

###### ROWの一致していない結果を出力
#for m in range(len(err_string2)):
#        print ("[ROW_ERROR]" + str(err_string2[m]))