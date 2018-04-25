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
import csv
#import math
import random
#import statistics
import re
#import openpyxl
import hashlib
import base64
#import binascii
pd.set_option('display.width', 600)  #数値を変更すると改行位置を変更できる


##############################
#### Sample Program
####   by Hidenobu Oguri   2017/08/07
####
#### Outline explanation
####   Read "T" file, and creates different Pseudonym IDs each of every month.
####   It can make some files, 
####         A(T) : IDs changes to Pseudonym IDs.
####         S    : Permuted Anonymized data without "DEL".
####         R    : Correspondence list of Real ID.
####         P    : Permuted row number of A(T) -> S.
####
#### How to use
####   python kamei.py T.csv
##############################



###  ファイルを読み込む
FILE1  = argv[1]
TRANS_MARK        = pd.read_csv(r"%s" % FILE1  , header=None , dtype={ 0:'S', 1:'S', 2:'S', 3:'S', 4:'S', 5:'S', 6:'S'}   )

## 期間ごとに，仮名IDの先頭文字に1月＝A，2月＝B,, の順にマークを付ける．
DIV_HEAD  = (
"0",
"A",
"B",
"C",
"D",
"E",
"F",
"G",
"H",
"I",
"J",
"K",
"L"
)

## IDをそのまま仮名化しないように，後ろに文字を付与してハッシュ化する（見えない）
## hashlib.md5(元ID ＋ DIV_APPEND[int(月)])  → 1月： A+md5(ID+JA)
## この値は利用者が個々に変更すること．
DIV_APPEND  = (
"0",
"JA",
"FE",
"MA",
"AP",
"MY",
"JN",
"JL",
"AU",
"SE",
"OC",
"NO",
"DE"
)




NEW_CODE = []

for i in range(len( TRANS_MARK[0] )):
#for i in range(100):
	if  TRANS_MARK[0][i]  == "DEL" :
		NEW_CODE.append( "DEL" )
	else:
		DIV_LINE = str(TRANS_MARK[2][i]).split("/") 
		DIV_CODE = int ( DIV_LINE[1] )
	
		## Pseudonym IDs  : 仮名が解るように加工する．システムは通ります．
		PsuIDS =  str( str( TRANS_MARK[0][i] ) + str(DIV_APPEND[DIV_CODE]) )
		## Encrypt IDs (!MD5) ：仮名を暗号化．しかしMD5なので脆弱性あり．
		#PsuIDS = hashlib.md5( str( str( TRANS_MARK[0][i] ) + str(DIV_APPEND[DIV_CODE]) ).encode('utf-8') ).hexdigest()
		
		NEW_CODE.append( str(DIV_HEAD[DIV_CODE]) + str(PsuIDS) )

TRANS_MARK['PsuID'] = NEW_CODE
FILENAME =  datetime.now().strftime("%H%M%S")









## A(T) ：行番号を変えないで出力する→これを匿名化フェイズでは提出する
TRANS_MARK.to_csv( 'AT_%s.csv' % FILENAME , sep=',', index=False, header=False, columns=['PsuID',1,2,3,4,5,6])










## S ：DEL行を除いて，行番号をランダムに変えたものをSとする．これは再識別フェイズに他ユーザに配布される．
TRANS_MARK1 =  TRANS_MARK[TRANS_MARK[0] != "DEL" ] 
TRANS_MARK1 =  TRANS_MARK1.reindex(np.random.permutation(TRANS_MARK1.index))
TRANS_MARK1.to_csv( 'S_%s.csv' % FILENAME , sep=',', index=False, header=False, columns=['PsuID',1,2,3,4,5,6])









## R ：Sにおける，各行の仮名化される前の本当のID．これが解ると再識別されてしまう．
TRANS_MARK1.to_csv( 'R_%s.csv' % FILENAME , sep=',', index=False, header=False, columns=[0])








P_ROW     = TRANS_MARK1.index
P_ROWLIST = []
for i in range(len( TRANS_MARK1.index )):
	P_ROWLIST.append( P_ROW[i] + 1 ) 

## P ：A(T)→Sに変換したときの行番号データ．これが解ると再識別されてしまう．
TRANS_MARK1["P"] = P_ROWLIST
TRANS_MARK1.to_csv( 'P_%s.csv' % FILENAME , sep=',', index=False, header=False, columns=["P"])






print(  TRANS_MARK1 )
print(  TRANS_MARK1.loc[:,[0,'PsuID']]  )




##行列の数を確認
YY,XX = TRANS_MARK.shape
print ( "S_%s.csv は %s 行 %s 列" % (FILENAME, YY,XX) ) 
print ( "経過時間：%s 秒" % round( time()-START  ,2 ) )
print ( "処理終了：%s" % datetime.now().strftime("%H:%M:%S") )


