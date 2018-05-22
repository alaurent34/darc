#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# calcurate difference of price between T, AT
# Author: Ryo Nojima
# J(M, T, AT) -> Utility score

# 価格の違いの平均

# 注意: 価格がfloatに変換できない文字列, あるいは<=0 であるとき
# エラーを出力し, 停止する.


import common,datetime,sys

def eval(M, T, T_0):
    if len(T_0)==0:
        sys.exit("Zero length T_0")

    price_score = 0.0

    for idx in range(len(T_0)):
        # T_0 と T の各行を配列に変換
        t_0 = T_0[idx].strip().split(',')
        t   = T[idx].strip().split(',')

        # 簡易 DEL チェッカー
        if t_0[0] == 'DEL': continue

        try:
            fl_t5 = float(t[5])
            fl_t05 = float(t_0[5])
            if fl_t5 < 0 or fl_t05 < 0:
                raise Exception
            # 値段の比率を罰則に加える.
            price_score += (1-min(fl_t5, fl_t05)/max(fl_t5, fl_t05))
        except:
            sys.exit("Price wrong format")

    # 正規化 最高0.0 最低1.0
    price_score = round(float(price_score)/float(len(T_0)),10)
    return price_score

if __name__ == '__main__':
    # 入力の受け取り
    M,T,T_0 = common.input(3)

    # 有用性評価
    price_score = eval(M,T,T_0)

    print(price_score, 'ut_price',sep=",")
