#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# common file for programs made by Ryo Nojima
# Author: Ryo Nojima

# version 0.4

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
        try:
            data.append(_pre_drop(feeded))
        except:
            sys.exit("Format Error")
    return data
