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
####   It can make some files.
####         A(T) : IDs changes to Pseudonym IDs.
####         S    : Permuted Anonymized data without "DEL".
####         R    : Correspondence list of Real ID.
####         P    : Permuted row number of A(T) -> S.
####
#### How to use
####   python kamei.py T.csv
##############################



FILE1      = argv[1]
TRANS_MARK = pd.read_csv(r"%s" % FILE1  , header = None , dtype = { 0:'S', 1:'S', 2:'S', 3:'S', 4:'S', 5:'S', 6:'S'}   )

## For each month, mark the first character of the pseudonymized ID with a letter. Expl: January = A, February = B
## The first character of the pseudonimized ID will be A if it buy something in Juanary.
## All the charachters stend for the month in the year : Jua -> A, Feb -> B, etc...
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
### We will append a character to the back of it so that it will not be converted to a pseudonym as it is (not visible)
### hashlib.md 5 (original ID + DIV_APPEND [int (month)]) → January: A + md 5 ID + JA)
### This value should be changed individually by the user.

## Basicaly represent the ending of the pseudonimized ID in function of the month
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

## Create pseudonymes for data T given in parameters
# For all rows in T
for i in range(len( TRANS_MARK[0] )):
    # Check if DEL (For T_alpha)
	if  TRANS_MARK[0][i]  == "DEL" :
		NEW_CODE.append( "DEL" )
	else:
        # Get Month of transaction
		DIV_LINE = str(TRANS_MARK[2][i]).split("/")
		DIV_CODE = int ( DIV_LINE[1] )

        # Create the second part of pseudo : ID + Month
		PsuIDS =  str( str( TRANS_MARK[0][i] ) + str(DIV_APPEND[DIV_CODE]) )

        # Append the all pseudonym too a list of code Letter + ID + Month
		NEW_CODE.append( str(DIV_HEAD[DIV_CODE]) + str(PsuIDS) )

# Affect the Pseudo to T in column PsuID
TRANS_MARK['PsuID'] = NEW_CODE
FILENAME =  datetime.now().strftime("%H%M%S")


## Write the AT file with the pseudonymes created above.
TRANS_MARK.to_csv( 'AT_%s.csv' % FILENAME , sep=',', index=False, header=False, columns=['PsuID',1,2,3,4,5,6])

# Create File S with DEL row removed and lines shuffled.
TRANS_MARK1 =  TRANS_MARK[TRANS_MARK[0] != "DEL" ]
TRANS_MARK1 =  TRANS_MARK1.reindex(np.random.permutation(TRANS_MARK1.index))
TRANS_MARK1.to_csv( 'S_%s.csv' % FILENAME , sep=',', index=False, header=False, columns=['PsuID',1,2,3,4,5,6])


## Create file R containing the ID <--> PsuID correspondance with S
TRANS_MARK1.to_csv( 'R_%s.csv' % FILENAME , sep=',', index=False, header=False, columns=[0])

P_ROW     = TRANS_MARK1.index
P_ROWLIST = []
for i in range(len( TRANS_MARK1.index )):
	P_ROWLIST.append( P_ROW[i] + 1 )

## Create file P : the order of the shuffle table S.
TRANS_MARK1["P"] = P_ROWLIST
TRANS_MARK1.to_csv( 'P_%s.csv' % FILENAME , sep=',', index=False, header=False, columns=["P"])

print(  TRANS_MARK1 )
print(  TRANS_MARK1.loc[:,[0,'PsuID']]  )

## YY -> size of database (#rows)
## XX -> size of attributes (#columns)
YY,XX = TRANS_MARK.shape
print ( "T_%s.csv in %s rows %s columns" % (FILENAME, YY,XX) )
print ( "execution time: %s" % round( time()-START  ,2 ) )
print ( "time now: %s" % datetime.now().strftime("%H:%M:%S") )


