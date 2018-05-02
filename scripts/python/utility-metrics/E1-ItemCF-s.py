# -*- coding: utf-8 -*-
#!/usr/bin/env python3

#create similarity matrix(W, W') and calcurate distance between W and W' (for supplier)
#Author: Takao Murakami, Masanori Monda
#Import: J(M, T, AT)
#Export: distance between W and W' (for supplier)

import sys
import math
import time
import pandas as pd


################################### パラメータ ###################################
# 購入数量-->スコアへの変換表
# 12個以上を1ダース単位にスコア化（1ダース→1，2ダース→2，3ダース→3，4ダース→4，5ダース→5，6ダース以上→6）
PurNum2Score = [12,24,36,48,60,72]
# Item-User辞書の各Itemにおけるユーザ数の閾値
UserNumThr = 1

######################### マスターデータの読み込みを行う関数 #########################
def ReadMasterData():
    # レコード数 --> m_size
    m_size = int(sys.stdin.readline().replace(('\r'or'\n'),'\r\n'))
    # マスターデータの読み込み
    for item in range(m_size):
        # 1行ずつ読み込み
       (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()

###################### トランザクションデータの読み込みを行う関数 #######################
# [戻り値1] total_user_num: User数
# [戻り値2] total_item_num: Item数
# [戻り値3] user_table: User変換表(User ID-->User No)
# [戻り値4] item_table: Item変換表(Item ID-->Item No)
# [戻り値5] user_item_dic: User-Item辞書
# [戻り値6] item_user_dic: Item-User辞書
def ReadTransData():
    # レコード数 --> t_size
    t_size = int(sys.stdin.readline().replace(('\r'or'\n'),'\r\n'))
    # 初期化
    total_user_num = 0
    total_item_num = 0
    user_table = {}
    item_table = {}
    user_item_dic = []
    item_user_dic = []
    # トランザクションデータの読み込み
    for item in range(t_size):
        # 1行ずつ読み込み
        item_string = (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()
        # User ID, Item ID, 購入数量 --> user_id, item_id, quantity
        item_list = item_string.split(",")
        user_id = item_list[0]
        item_id = item_list[4]
        quantity = int(item_list[6])
        # quantity = 1 とすると，購入回数になる
        #quantity = 1
        # User ID(user_id)がUser変換表(user_table)に含まれていない場合
        if user_id not in user_table:
            # User変換表(user_table)に User ID:User No (user_id:total_user_num) を追加
            user_table[user_id] = total_user_num
            # User No(total_user_num)に対応するUser-Item辞書(user_item_dic[total_user_num])を初期化
            user_item_dic.append({})
            # User No(total_user_num)を1増やす
            total_user_num += 1
        # Item ID(item_id)がItem変換表(item_table)に含まれていない場合
        if item_id not in item_table:
            # Item変換表(item_table)に Item ID:Item No (item_id:total_item_num) を追加
            item_table[item_id] = total_item_num
            # Item No(total_item_num)に対応するItem-User辞書(item_user_dic[total_item_num])を初期化
            item_user_dic.append({})
            # Item No(total_item_num)を1増やす
            total_item_num += 1
        # 現在のUser No --> user_no
        user_no = user_table[user_id]
        # 現在のItem No --> item_no
        item_no = item_table[item_id]
        # Item-User辞書の更新 --> item_user_dic
        # User No(user_no)がItem-User辞書(item_user_dic[item_no])に含まれていない場合
        if user_no not in item_user_dic[item_no]:
            # Item-User辞書(item_user_dic[item_no])に User No:購入数量 (user_no:quantity) を追加
            item_user_dic[item_no][user_no] = quantity
        # User No(user_no)がItem-User辞書(item_user_dic[item_no])に含まれている場合
        else:
            # Item-User辞書(item_user_dic[item_no])に 対応するUser No(user_no)の購入数量をquantityだけ増やす
            item_user_dic[item_no][user_no] += quantity
    #item_user_dic_original = item_user_dic
    # Item-User辞書において，購入数量 --> スコアへの変換を行う (スコアが0の要素は削除する)
    for item_no in range(len(item_user_dic)):
        for user_no in list(item_user_dic[item_no]):
            score = 0
            for elem in range(len(PurNum2Score)):
                if item_user_dic[item_no][user_no] < PurNum2Score[elem]:
                    break
                else:
                    score += 1
            item_user_dic[item_no][user_no] = score
            # スコアが0の要素は削除する
            if item_user_dic[item_no][user_no] == 0:
                del item_user_dic[item_no][user_no]
    # Item-User辞書の各Itemにおいて，ユーザ数がUserNumThr未満のものは削除する
    for item_no in range(len(item_user_dic)):
        if len(item_user_dic[item_no]) < UserNumThr:
            for user_no in list(item_user_dic[item_no]):
                del item_user_dic[item_no][user_no]
    # Item-User辞書からUser-Item辞書を作成する --> user_item_dic
    for item_no in range(len(item_user_dic)):
        for user_no,score in item_user_dic[item_no].items():
            user_item_dic[user_no][item_no] = score
    return (total_user_num, total_item_num, user_table, item_table, user_item_dic, item_user_dic)

################### 匿名加工トランザクションデータの読み込みを行う関数 ###################
# [戻り値1] total_user_num: User数
# [戻り値2] user_table: User変換表(User ID-->User No)
# [戻り値3] user_item_dic: User-Item辞書
# [戻り値4] item_user_dic: Item-User辞書
# [引数] item_table: Item変換表(Item ID-->Item No)
def ReadAnonyTransData(item_table):
    # レコード数 --> t_size
    t_size = int(sys.stdin.readline().replace(('\r'or'\n'),'\r\n'))
    # 初期化
    total_user_num = 0
    user_table = {}
    user_item_dic = []
    item_user_dic = []
    for item_id in item_table.keys():
        item_user_dic.append({})
    # トランザクションデータの読み込み
    for item in range(t_size):
        # 1行ずつ読み込み
        item_string = (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()
        # User ID, Item ID, 購入数量 --> user_id, item_id, quantity
        item_list = item_string.split(",")
        user_id = item_list[0]
        item_id = item_list[4]
        # T0においてUser IDが’DEL’になっている行はスキップする
        if user_id == 'DEL':
            continue
        quantity = int(item_list[6])
        # quantity = 1 とすると，購入回数になる
        #quantity = 1
        # User ID(user_id)がUser変換表(user_table)に含まれていない場合
        if user_id not in user_table:
            # User変換表(user_table)に User ID:User No (user_id:total_user_num) を追加
            user_table[user_id] = total_user_num
            # User No(total_user_num)に対応するUser-Item辞書(user_item_dic[total_user_num])を初期化
            user_item_dic.append({})
            # User No(total_user_num)を1増やす
            total_user_num += 1
        # 現在のUser No --> user_no
        user_no = user_table[user_id]
        # 現在のItem No --> item_no
        if item_id in item_table:
            item_no = item_table[item_id]
        # T1には存在しないItemの場合は，飛ばす
        else:
            continue
        # Item-User辞書の更新 --> item_user_dic
        # User No(user_no)がItem-User辞書(item_user_dic[item_no])に含まれていない場合
        if user_no not in item_user_dic[item_no]:
            # Item-User辞書(item_user_dic[item_no])に User No:購入数量 (user_no:quantity) を追加
            item_user_dic[item_no][user_no] = quantity
        # User No(user_no)がItem-User辞書(item_user_dic[item_no])に含まれている場合
        else:
            # Item-User辞書(item_user_dic[item_no])に 対応するUser No(user_no)の購入数量をquantityだけ増やす
            item_user_dic[item_no][user_no] += quantity
    # Item-User辞書において，購入数量 --> スコアへの変換を行う (スコアが0の要素は削除する)
    for item_no in range(len(item_user_dic)):
        for user_no in list(item_user_dic[item_no]):
            score = 0
            for elem in range(len(PurNum2Score)):
                if item_user_dic[item_no][user_no] < PurNum2Score[elem]:
                    break
                else:
                    score += 1
            item_user_dic[item_no][user_no] = score
            # スコアが0の要素は削除する
            if item_user_dic[item_no][user_no] == 0:
                del item_user_dic[item_no][user_no]
    # Item-User辞書の各Itemにおいて，ユーザ数がUserNumThr未満のものは削除する
    for item_no in range(len(item_user_dic)):
        if len(item_user_dic[item_no]) < UserNumThr:
            for user_no in list(item_user_dic[item_no]):
                del item_user_dic[item_no][user_no]
    # Item-User辞書からUser-Item辞書を作成する --> user_item_dic
    for item_no in range(len(item_user_dic)):
        for user_no,score in item_user_dic[item_no].items():
                user_item_dic[user_no][item_no] = score
    return (total_user_num, user_table, user_item_dic, item_user_dic)


###################### 2つのItemのCosine類似度を計算する関数 ######################
# [戻り値] cosine類似度
# [引数1] item_user_dic: Item-User辞書
# [引数2] item_no: 1つ目のItem No
# [引数2] item2_no: 2つ目のItem No
def CalcCosSim(item_user_dic, item_no, item2_no):
    # 初期化
    cos_sim = 0
    item_vec_size = 0
    item2_vec_size = 0
    inner_product = 0
    # Item-User辞書の1つ目のItem No
    for user_no,score in item_user_dic[item_no].items():
        # 1つ目のItemの特徴ベクトルのサイズを更新 --> item_vec_size
        item_vec_size += score*score
        # 2つ目のItemの特徴ベクトルにuser_noが含まれていれば，Item同士の内積を更新 --> inner_product
        if user_no in item_user_dic[item2_no]:
            score2 = item_user_dic[item2_no][user_no]
            inner_product += score*score2
    # Item-User辞書の2つ目のItem No
    for user_no,score2 in item_user_dic[item2_no].items():
        # 2つ目のItemの特徴ベクトルのサイズを更新 --> item2_vec_size
        item2_vec_size += score2*score2
    # cosine類似度を計算
    cos_sim = float(inner_product) / float(math.sqrt(item_vec_size) * math.sqrt(item2_vec_size))
    return cos_sim


############# Item-User/User_Item辞書からItem-Item辞書を作成する関数 ##############
# [戻り値] item_item_dic: Item-Item辞書
# [引数1] user_item_dic: User-Item辞書
# [引数2] item_user_dic: Item-User辞書
def CalcItem2ItemDic(user_item_dic, item_user_dic):
    # 初期化
    item_item_dic = {}
    # Item-User/User_Item辞書から，denseなところを1に初期化したItem-Item辞書を作成する --> item_item_dic
    for item_no in range(len(item_user_dic)):
        for user_no in item_user_dic[item_no].keys():
            for item2_no in user_item_dic[user_no].keys():
                 if item_no != item2_no:
                    # Item-Item辞書のキー(item_no,item2_no)に対応する値を1に初期化
                    item_item_dic[(item_no,item2_no)] = 1
    # Item-Item辞書のうちdenseなところについて，cosine類似度を求める
    for item_no,item2_no in item_item_dic.keys():
        item_item_dic[(item_no,item2_no)] = CalcCosSim(item_user_dic,item_no,item2_no)

    return item_item_dic

############################ 類似度行列の距離の計算 #############################
# [戻り値] sim_dist: 類似度行列の距離
# [引数1] item_item_dic: Item-Item辞書(T1)
# [引数2] item_item_dic: Item-Item辞書(T2)
def CalcSimMatDist(item_item_dic1, item_item_dic2):
    # 初期化
    sim_dist = 0
    item_item_dic1_sum = 0
    # Item-Item辞書(T1)のdenseな要素から距離を計算
    for item_no,item2_no in item_item_dic1:
        # Item-item辞書(T1)の要素の総和 --> item_item_dic1_sum
        item_item_dic1_sum += item_item_dic1[(item_no,item2_no)]
        # Item-Item辞書(T2)においてもdenseな場合
        if (item_no,item2_no) in item_item_dic2:
            # L1距離
            sim_dist += math.fabs(item_item_dic1[(item_no,item2_no)] - item_item_dic2[(item_no,item2_no)])
        # Item-Item辞書(T2)ではsparseな場合
        else:
            # L1距離
            sim_dist += item_item_dic1[(item_no,item2_no)]
    # Item-item辞書(T1)の要素の総和で割ることで正規化
    sim_dist /= item_item_dic1_sum
    # 正規化後の距離が1を超えた場合は，1にする
    if sim_dist > 1.0:
        sim_dist = 1.0
    return sim_dist

############################## 入力データの読み込み ##############################
# 時間計測スタート
start = time.time()

# マスターMの読み込み
ReadMasterData()

# トランザクションTの読み込み
total_user_num1, total_item_num1, user_table1, item_table1, user_item_dic1, item_user_dic1 = ReadTransData()

# トランザクションTのItem-Item辞書を作成する
item_item_dic1 = CalcItem2ItemDic(user_item_dic1, item_user_dic1)

# トランザクションT0の読み込み
total_user_num2, user_table2, user_item_dic2, item_user_dic2 = ReadAnonyTransData(item_table1)

# トランザクションT0のItem-Item辞書を作成する
item_item_dic2 = CalcItem2ItemDic(user_item_dic2, item_user_dic2)

########################## 類似度行列の距離の計算・出力 ##########################
# 類似度行列の距離 --> sim_dist
sim_dist = CalcSimMatDist(item_item_dic1, item_item_dic2)
# 出力
#print('%f' % sim_dist)
print('%f' % sim_dist + ',ut-ItemCF-supply')

# debug用
# 実行時間を表示
elapsed_time = time.time() - start
#print('Time: {0}'.format(elapsed_time) + '[sec]')
###############################################################################
