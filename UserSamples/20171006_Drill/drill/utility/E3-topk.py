# -*- coding: utf-8 -*-
#!/usr/bin/env python3

#create create top-k items list, and calcurate distance between W, W'(only configured from top-k items)
#Author: Takao Murakami, Masanori Monda
#Import: J(M, T, AT)
#Export: top-k items list, distance between W, W'(only configured from top-k items)

import sys
import math
import time
import pandas as pd
import csv

################################## パラメーター ##################################
# 購入した顧客数が上位kとなるアイテムについて有用性を評価する
k = 100

######################### マスターデータの読み込みを行う関数 #########################
def ReadMasterData():
    # レコード数 --> m_size
    m_size = int(sys.stdin.readline().replace(('\r'or'\n'),'\r\n'))
    # マスターデータの読み込み
    for item in range(m_size):
        # 1行ずつ読み込み
       (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()

###################### トランザクションデータの読み込みを行う関数(1) #######################
# [戻り値1] item_table: Item変換表(Item ID-->Item No)
# [戻り値2] user_item_dic: User-Item辞書
# [戻り値3] item_user_dic: Item-User辞書
# [戻り値4] T_data: ReadTransData2で利用するためのトランザクションデータのコピー
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
    T_data = []
    # トランザクションデータの読み込み
    for item in range(t_size):
        # 1行ずつ読み込み
        item_string = (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()
        # User ID, Item ID, 購入数量 --> user_id, item_id, quantity
        item_list = item_string.split(",")
        T_data.append(item_list)
        user_id = item_list[0]
        item_id = item_list[4]
        quantity = int(item_list[6])
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
            item_user_dic[item_no][user_no] = 1

    return (item_table, user_item_dic, item_user_dic, T_data)


################### 匿名加工トランザクションデータの読み込みを行う関数(1) ###################
# [戻り値1] item_user_dic: Item-User辞書
# [戻り値2] T0_data: ReadAnonyTransData2で利用するための匿名加工トランザクションデータのコピー
# [引数] item_table: Item変換表(Item ID-->Item No)
def ReadAnonyTransData(item_table):
    # レコード数 --> t_size
    t_size = int(sys.stdin.readline().replace(('\r'or'\n'),'\r\n'))
    # 初期化
    total_user_num = 0
    user_table = {}
    user_item_dic = []
    item_user_dic = []
    T0_data = []
    for item_id in item_table.keys():
        item_user_dic.append({})
    # トランザクションデータの読み込み
    for item in range(t_size):
        # 1行ずつ読み込み
        item_string = (sys.stdin.readline().replace(('\r'or'\n'),'\r\n')).strip()
        # User ID, Item ID, 購入数量 --> user_id, item_id, quantity
        item_list = item_string.split(",")
        T0_data.append(item_list)
        user_id = item_list[0]
        if user_id == 'DEL':
            continue
        item_id = item_list[4]
        quantity = int(item_list[6])
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
            item_user_dic[item_no][user_no] = 1

    # Item-User辞書からUser-Item辞書を作成する --> user_item_dic
    for item_no in range(len(item_user_dic)):
        for user_no,score in item_user_dic[item_no].items():
                user_item_dic[user_no][item_no] = score

    return (item_user_dic, T0_data)

###################### トランザクションデータの読み込みを行う関数(2) #######################
# [戻り値1] total_user_num: User数
# [戻り値2] total_item_num: Item数
# [戻り値3] user_table: User変換表(User ID-->User No)
# [戻り値4] item_table: Item変換表(Item ID-->Item No)
# [戻り値5] user_item_dic: User-Item辞書
# [戻り値6] item_user_dic: Item-User辞書
# [引数1] T_data: トランザクションデータ
# [引数2] top_k_ids: トランザクションデータにおいて購入顧客数が上位k位となる商品IDリスト
def ReadTransData2(T_data, top_k_ids):
    # 初期化
    total_user_num = 0
    total_item_num = 0
    user_table = {}
    item_table = {}
    user_item_dic = []
    item_user_dic = []
    # トランザクションデータの読み込み
    for item_list in T_data:
        # 1行ずつ読み込み
        # User ID, Item ID, 購入数量 --> user_id, item_id, quantity
        user_id = item_list[0]
        item_id = item_list[4]
        if item_id not in top_k_ids:
            continue
        quantity = int(item_list[6])
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
            item_user_dic[item_no][user_no] = 1

    # Item-User辞書からUser-Item辞書を作成する --> user_item_dic
    for item_no in range(len(item_user_dic)):
        for user_no,score in item_user_dic[item_no].items():
            user_item_dic[user_no][item_no] = score

    return (total_user_num, total_item_num, user_table, item_table, user_item_dic, item_user_dic)


################### 匿名加工トランザクションデータの読み込みを行う関数(2) ###################
# [戻り値1] total_user_num: User数
# [戻り値2] user_table: User変換表(User ID-->User No)
# [戻り値3] user_item_dic: User-Item辞書
# [戻り値4] item_user_dic: Item-User辞書
# [引数1] T0_data: 匿名加工トランザクションデータ
# [引数2] top_k_ids: トランザクションデータにおいて購入顧客数が上位k位となる商品IDリスト
def ReadAnonyTransData2(T0_data, item_table, top_k_ids):
    # 初期化
    total_user_num = 0
    user_table = {}
    user_item_dic = []
    item_user_dic = []
    for item_id in item_table.keys():
        item_user_dic.append({})
    # トランザクションデータの読み込み
    for item_list in T0_data:
        # 1行ずつ読み込み
        user_id = item_list[0]
        if user_id == 'DEL':
            continue
        item_id = item_list[4]
        if item_id not in top_k_ids:
            continue
        quantity = int(item_list[6])
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
            item_user_dic[item_no][user_no] = 1

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

############### Item-User辞書からTOPkのItemリストを作成する関数 ################
# [戻り値] 購入顧客数が上位k位の商品Noのリスト（元々の商品IDではない）
# [引数] item_user_dic: Item-User辞書
def MakeTopkItemList(item_user_dic, item_table):
        frequent_item_dic = {}
        top_k_items = []
        for tmp_id in range(len(item_user_dic)):
            bought_num = 0
            bought_num = len(item_user_dic[tmp_id])
            for i, j in item_table.items():
                if j == tmp_id:
                    item_id = i
            frequent_item_dic[item_id] = bought_num
        frequent_item_dic = sorted(frequent_item_dic.items(), key=lambda x:(x[1],x[0]), reverse=True)
        #print(frequent_item_dic)
        top_k = frequent_item_dic[:k]
        for l in range(len(top_k)):
            top_k_items.append(top_k[l][0])
        return(top_k_items)

############### Item-table からTOPkのItemリストを商品IDに戻す関数 ################
# [戻り値] 購入顧客数が上位k位の商品IDのリスト
# [引数1] top_k_items: Item-User辞書
# [引数2] item_table: Item変換表(Item ID-->Item No)
def TopkIDList(top_k_items, item_table):
        top_k_ids = []
        for item in top_k_items:
            for item_id, item_no in item_table.items():
                if item_no == item:
                    top_k_ids.append(item_id)
        return(top_k_ids)

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
#start = time.time()

# マスターMの読み込み
ReadMasterData()

# トランザクションTの読み込み
item_table1, user_item_dic1, item_user_dic1, T_data = ReadTransData()

# トランザクションTのTOPkアイテムリストを作成する
top_k_items1 = MakeTopkItemList(item_user_dic1, item_table1)
#print(top_k_items1)

# トランザクションT0の読み込み
item_user_dic2, T0_data = ReadAnonyTransData(item_table1)

# トランザクションT0のTOPkアイテムリストを作成する
top_k_items2 = MakeTopkItemList(item_user_dic2, item_table1)

# TOPkリストの距離 --> top_k_dist
# top_k_items1とtop_k_items2の差集合を計算
top_k_dist = len(set(top_k_items1).difference(set(top_k_items2))) / k
print('%f' % top_k_dist + ',topk_list_difference')

# Tから作成したTOPkアイテムを元にトランザクションTの再読み込み
total_user_num1, total_item_num1, user_table1, item_table1, user_item_dic1, item_user_dic1 = ReadTransData2(T_data, top_k_items1)

# トランザクションTのItem-Item辞書を作成する
item_item_dic1 = CalcItem2ItemDic(user_item_dic1, item_user_dic1)

# Tから作成したTOPkアイテムを元にトランザクションT0の再読み込み
total_user_num2, user_table2, user_item_dic2, item_user_dic2 = ReadAnonyTransData2(T0_data, item_table1, top_k_items1)

# トランザクションT0のItem-Item辞書を作成する
item_item_dic2 = CalcItem2ItemDic(user_item_dic2, item_user_dic2)

# 類似度行列の距離 --> sim_dist
sim_dist = CalcSimMatDist(item_item_dic1, item_item_dic2)
print('%f' % sim_dist + ',similarity_distance')

# 実行時間を表示
#elapsed_time = time.time() - start
#print('{:.3f}'.format(elapsed_time))
#print('実行時間：' + '{:.3f}'.format(elapsed_time) + '[sec]')
