#coding:utf-8
from time import time
START = time()
from datetime import datetime

import sys
from sys import argv
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import csv
pd.set_option('display.width', 600)  #数値を変更すると改行位置を変更できる


##############################
#### Sample Program
####   by Hidenobu Oguri   2017/08/07
####   edit by Akari Tachibana   2017/08/28
####   edit by Masanori Monda 2017/10/04
####
#### Outline explanation
####   Read "F","Fh"  files, and calculate the Match rate (= New Definition of Re-Identify rate).
####
#### How to use
####   python compare_and.py FILE1 FILE2
##############################


# 引数の定義と格納
ARGS = []
for i in range(len(argv)):
	ARGS.append(argv[i])
NUM_ARGS = len(ARGS)
FILE1  = ARGS[1]
FILE2  = ARGS[2]

##### FILE1をpandasに展開
MASTER_DATA1 = []
for line in open( FILE1 , 'r'):
	itemList = line[:-1].split(',')
	MASTER_DATA1.append(itemList)
MASTER_MAP = pd.DataFrame(MASTER_DATA1)

##### FILE2のチェック
flg = 0
f = open(FILE2, 'r')
first_key = int(f.readline()[:3])
if first_key == 500:
	flg = 1
##### FILE2をpandasに展開
if flg == 1:
	INPUT_DATA1 = []
	count = 0
	for line in open( FILE2 , 'r'):
		if count > 0:
			itemList = line[:-1].split(',')
			INPUT_DATA1.append(itemList)
		count += 1
	INPUT_MAP = pd.DataFrame(INPUT_DATA1)
else:
	INPUT_DATA1 = []
	for line in open( FILE2 , 'r'):
		itemList = line[:-1].split(',')
		INPUT_DATA1.append(itemList)
	INPUT_MAP = pd.DataFrame(INPUT_DATA1)

###### ファイルをそれぞれ分割したまででタイム
HALF_TIME = time()


##### データをソートして，Fhデータに関してはインデックスを振りなおす
MASTER_MAP = MASTER_MAP.sort_values(by=[0], ascending=True)
INPUT_MAP  = INPUT_MAP.sort_values(by=[0], ascending=True)
INPUT_MAP  = INPUT_MAP.reset_index(drop=True)

#####################
##### MAPの比較 #####
#####################

## MASTERの母数算出
YY,XX = MASTER_MAP.shape # 500, 13
ALL_NUM = YY

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


POINT = 0
BINGO = 0
ERR   = ""

## その後，INPUTデータとMASTERデータの各列の一致数を調査
if(map_error == 0):
	for ii in range(len(MASTER_MAP[0])):
		for i in range(1,XX):
			### 各値の一致数をカウント
			if MASTER_MAP[i][ii] == INPUT_MAP[i][ii]  :
				POINT = POINT + 1
				if POINT == (XX - 1) :
					BINGO = BINGO + 1
					POINT = 0
			else :
				POINT = 0
				ERR = ERR + "\n" + (str (MASTER_MAP[0][ii]) + ":(" + str (i) + "," + str (ii) + ")" + str (MASTER_MAP[i][ii]) + "<->" + str( INPUT_MAP[i][ii] ))
				break

###### MAPの比較完了までのタイム
END_MAP_COMPARE = time()



#####################
##### 結果 出力 #####
#####################

###### MAPの一致率結果と算出時間出力
if(map_error == 0):
	#print ( "[MAP]Result,Time:" + str(round(float(BINGO)/float(ALL_NUM), 6)) + "," + str(round( (END_MAP_COMPARE - HALF_TIME) + (HALF_TIME - START)  ,2 )))
	print (str(round(float(BINGO)/float(ALL_NUM), 6)))
else:
	print ( "[MAP]Result,Time:0.0," + str(round( (END_MAP_COMPARE - HALF_TIME) + (HALF_TIME - START)  ,2 )))

#print("母数:" + str(ALL_NUM))
#print("成功:" + str(BINGO))
#print("不正解リスト:" + str(ERR))
