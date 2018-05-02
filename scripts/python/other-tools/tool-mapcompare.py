#coding:utf-8
from time import time
START = time()
from datetime import datetime
###print ("処理開始：%s" % START.strftime("%H:%M:%S.")  + "%02d" % (START.microsecond // 1000))
###print  ("経過時間：%s 秒" % round( time() - START  ,2 ) )

from sys import argv
#import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import pandas.tools.plotting as plotting
#import matplotlib.pyplot as plt
import csv
#import math
import random
#import statistics
import re
#import openpyxl
#import hashlib
#import base64
pd.set_option('display.width', 600)  #数値を変更すると改行位置を変更できる


##############################
#### Sample Program
####   by Hidenobu Oguri   2017/08/07
####
#### Outline explanation
####   Read "F","Fhat"  files, and calculate the Match rate (= Re-Identify rate 1).
#### 
#### How to use
####   python mapcompare.py F.csv Fh.csv
##############################


# 引数の定義と格納
ARGS = []
for i in range(len(argv)):
	ARGS.append(argv[i])
NUM_ARGS = len(ARGS)

FILE1  = ARGS[1]
FILE2  = ARGS[2]

MAP_MASTER            = pd.read_csv(r"%s" % FILE1  , header=None)
MAP_INPUT             = pd.read_csv(r"%s" % FILE2  , header=None)


YY,XX = MAP_MASTER.shape # 600, 13
ALL_NUM = YY * (XX-1)



## まず，INPUTデータとMASTERデータのID列が同じであるかを調査
for i in range(len(MAP_MASTER[0])):
	if MAP_MASTER[0][i] != MAP_INPUT[0][i]  :
		print ( "NG : Number of lines is not same." )
		sys.exit()




### エラー格納用配列
err_string = []

## その後，INPUTデータとMASTERデータの各列の一致数を調査
POINT = 0
DEL   = 0
for i in range(1,13):
	for ii in range(len(MAP_MASTER[0])):
		if MAP_MASTER[i][ii] == MAP_INPUT[i][ii]  :
			POINT = POINT + 1
		if MAP_MASTER[i][ii] == "DEL":
			DEL   = DEL + 1
		else :
			#print ( "Error: " + str(i) + "列" + str(ii) + "行 " +  str(MAP_MASTER[i][ii]) + " -> " + str( MAP_INPUT[i][ii] ) ) 
                        err_string.append( "Error : " + str(i) + "列" + str(ii) + "行 " +  str(MAP_MASTER[i][ii]) + " -> " + str( MAP_INPUT[i][ii] ) ) 

###### MAPの比較完了までのタイム
END_MAP_COMPARE = time()




print ( "Total       :" +  str(ALL_NUM))
print ( "Match       :" +  str( POINT ) )
print ( "Result      :" +  str(round(float(POINT)/float(ALL_NUM),2)))
print ( "DEL(MASTER) :" +  str( DEL ) )
print ( "経過時間 : %s 秒" % round( time()-START  ,2 ) )


##エラー（一致していない）結果を出力
#for n in range(len(err_string)):
#        print (err_string[n])

