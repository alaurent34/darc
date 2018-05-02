#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# calcurate difference of date between T, AT
# Author: Ryo Nojima
# J(M, T, AT) -> Utility score

# T, ATの日付差の平均

# 注意: 価格がfloatに変換できない文字列, あるいは<=0 であるとき
# エラーを出力し, 停止する.


import common,datetime,sys

def eval(M, T, T_0):
    if len(T_0)==0:
        sys.exit("Zero length T_0")

    date_score = 0

    for idx in range(len(T_0)):
        # T_0 と T の各行を配列に変換
        t_0 = T_0[idx].strip().split(',')
        t   = T[idx].strip().split(',')

        # 簡易 DEL チェッカー
        if t_0[0] == 'DEL': continue

        # 各行から日付を抽出
        try:
            t_0_day = datetime.datetime.strptime(t_0[2], '%Y/%m/%d')
            t_day = datetime.datetime.strptime(t[2], '%Y/%m/%d')
        except:
            sys.exit("Date wrong format")

        # 日付の差を計算し, 罰則を加える
        date_score += abs((t_day - t_0_day).days)

    # 正規化 最高0.0 最低1.0
    date_score = round(float(date_score)/float(31 * len(T_0)),10)
    return date_score

if __name__ == '__main__':
    # 入力の受け取り
    M,T,T_0 = common.input(3)

    # 有用性評価
    data_score = eval(M,T,T_0)

    print(data_score, 'ut_date',sep=",")
