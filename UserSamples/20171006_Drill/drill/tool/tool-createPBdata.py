# -*- coding: utf-8 -*-

from datetime import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import pandas.tools.plotting as plotting
pd.set_option('display.width', 400)  #数値を変更すると改行位置を変更できる
import re
import hashlib
import math
import sys
from sys import argv
import io
import os

###############
#  How to use
#  type AT_file.txt | python createPBdata.py S_file.txt
###############

# 標準入出力の文字コードを明示的に指定
# apacheユーザで実行するとデフォルトでANSI_X3.4-1968になってしまうのため
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

###############
### 引数取得
ARGS = []
for i in range(len(argv)):
    ARGS.append(argv[i])
NUM_ARGS = len(ARGS)
#logger.info('[get args] ' + (' '.join(ARGS)))

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
#logger.info('[get stdin and convert to dataframe]')

##Noneの値を含む行を削除(行番号はそのまま保持される)
DATA = DATA.dropna()
##DELを含まない行を抽出する(行番号はそのまま保持される)
DATA = DATA[DATA[0] != 'DEL']
#logger.info('[delete DEL lines]')

### ランダムソート
DATA = DATA.reindex(np.random.permutation(DATA.index))

### Sを出力
DATA.to_csv(OUTPUT_FILE[0], sep=',', index=False, header=False)
#logger.info('[output]' + str(OUTPUT_FILE[0]) )

#print ("outputpath1:" + str(OUTPUT_FILE[0]) )
