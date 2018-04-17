#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使い方: cat MT | このプログラム
#   ただし, MTは, Mの行数, M, Tの行数, Tで構成
# 処理: 月単位で仮名化
# 出力: M, T, T_0  (T_0は仮名を付与したのみ)

import random, copy, common, os


# Algorithm P by Knuth
# given a list a, output random shuffle of a 
## please check wiki
def algorithm_P(a):
    for i in range(len(a)-1, 0, -1):
        # 暗号用に/dev/urandom を利用 
        # random.SystemRandom().shuffle でもいけると思うが, 
        # メルセンヌツイスターを使っている可能性があるため最低限にしておく
        j = random.SystemRandom().randint(0, i)
        tmp = a[i]
        a[i] = a[j]
        a[j] = tmp
    return a

# 仮名生成を行う
def kamei_gen(M):
    # 顧客IDのリスト (Mに線形オーダー)
    cus_ids = [cus.split(',')[0] for cus in M]

    # 1顧客に月単位で仮名を生成する
    kamei = []
    for month in range(12):
        kamei_month = list(range(0, len(cus_ids)))
        algorithm_P(kamei_month)
        kamei.append(copy.deepcopy(kamei_month))
    
    kamei_dict = {}
    for idx in range(len(cus_ids)):
        kamei_dict[cus_ids[idx]] = [str(kamei[month][idx]) for month in range(12)]
    return kamei_dict

def month_passed(date):
    return int(date.split('/')[1])-1
    
def kakou(M, T):
    kamei_dict = kamei_gen(M)
    T_0 = []
    for gyo in range(len(T)):
        T_gyo = T[gyo].strip().split(',')
        T_gyo[0] = kamei_dict[T_gyo[0]][month_passed(T_gyo[2])]
        T_0.append(','.join(T_gyo))
    return M,T,T_0

if __name__ == '__main__':
    # 元データであるマスターとトランザクションを受け取る
    M,T = common.input(2)
    
    # M, T を加工する
    M,T,T_0 = kakou(M,T)

    # M, T, T_0 を出力する
    common.output([M,T,T_0])

