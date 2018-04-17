#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# version 0.1 by RN
# version up 頼んだ

import sys, datetime, random

# フォーマットを整えて出力する.
def output(just_list):
    for index in range(len(just_list)):
        print(len(just_list[index]))
        print(('\n').join(just_list[index]))

# 入力数を受け取り, num個をリストに格納し, retする.
def input(num):
    # 入力から先頭のデータを取り出す.
    def _pre_drop(len_con_rem):
        """
        入力 (len_con_rem) : con の長さ, con そのもの, 残り rem
        返却 con (ただし, rem はそのまま残る) 
        """
        con = len_con_rem[1: int(len_con_rem[0])+1]
        del len_con_rem[0: int(len_con_rem[0])+1]
        return con
    
    data = []    
    # 一つのリストとして入力を読み込む
    feeded = list(map(lambda x: x.strip(), sys.stdin.readlines()))

    # num 個 の入力をdataに保存
    for _ in range(num):
        data.append(_pre_drop(feeded))
    return data

# データセット初日
beg = datetime.datetime.strptime('2010/12/1', '%Y/%m/%d')
# データセット最終日
fin = datetime.datetime.strptime('2011/12/9', '%Y/%m/%d')

# データセット、中央日。仮名化の際は, 2011/6/6以降（後期）と
# 以前(前期)で異なる仮名を付与している. 2011/6/6は後期にしている.
mid = datetime.datetime.strptime('2011/6/6', '%Y/%m/%d')

# データセット初日から最終までの日数
span = (fin - beg).days

# hizuke が 2010/12/1 -- 2011/12/9 の間に入っていればTrue (両端含む)
def safty_date(hizuke):
    check_date = datetime.datetime.strptime(hizuke, '%Y/%m/%d')
    if (check_date - beg).days >= 0 and (fin - check_date).days >= 0:
        return True
    return False

# hizuke が 2011/6/6 以降であれば1 (2011/6/6を含む)
#                      それ以外は0
def zenki_or_kouki(hizuke):
    check_date = datetime.datetime.strptime(hizuke, '%Y/%m/%d')
    if (check_date - mid).days >= 0:
        return 1  # kouki
    return 0      # zenki

# 仮名生成を行う
def kamei_gen(M):
    # 顧客IDのリスト (Mに線形オーダー)
    cus_ids = [cus.split(',')[0] for cus in M]
    # 1顧客に2個の仮名を準備 (|M|log|M|オーダー程度)
    kamei0 = list(range(0, len(cus_ids)))
    random.shuffle(kamei0)
    kamei1 = list(range(0, len(cus_ids)))
    random.shuffle(kamei1)
    kamei_dict = {}
    for idx in range(len(cus_ids)):
        kamei_dict[cus_ids[idx]] = (str(kamei0[idx]), str(kamei1[idx]))
    return kamei_dict
