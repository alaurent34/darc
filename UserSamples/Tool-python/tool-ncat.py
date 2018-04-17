#!/usr/bin/env python
import sys

def read_write_table(csvfile):
    # ファイル行数出力
    num_lines = sum(1 for line in open(csvfile))
    print(num_lines)
    # ファイル内容出力
    f = open(csvfile, "r")
    for line in f:
        print(line, end="")

        
# コマンドライン引数を格納したリストの取得
argvs = sys.argv
# 各ファイルを読み込み，行数を付与して，連結形式として標準出力
read_write_table(argvs[1])
read_write_table(argvs[2])
read_write_table(argvs[3])
#read_write_table(argvs[4])
