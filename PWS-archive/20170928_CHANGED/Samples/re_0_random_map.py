# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# reidentify by exact month
# J(M, S, T^\alpha) -> f-hat
# how to use: cat J_***.txt | python re_0_random_map.py

# (c) 2017 Masanori Monda, Ryo Nojima

# 以下，仮名表Fのことをmapと呼ぶ

import common
import random
import csv

################ 入力 ################
M, S, T_alpha = common.input(3)


################ マスターデータ，部分知識T_alpha から，推定mapの枠組みを作成 ################

##### Mから推定map(re_map)の土台(すべてDEL)re_map_baseを作成する #####
re_map_base = {}
for item in range(len(M)):
    item_string = (M[item].replace(('\r'or'\n'),'\r\n')).strip()
    item_list = item_string.split(",")
    user_id = item_list[0]
    if user_id not in re_map_base:
        re_map_base[user_id] = ['DEL','DEL','DEL','DEL','DEL','DEL','DEL','DEL','DEL','DEL','DEL','DEL']

##### T_alphaに購買履歴がある月について，re_map_baseの要素を空にする( 'DEL' => '' ) #####

for item in range(len(T_alpha)):
    item_string = (T_alpha[item].replace(('\r'or'\n'),'\r\n')).strip()
    item_list = item_string.split(",")
    user_id = item_list[0]
    if user_id == 'DEL':
        continue
    date = item_list[2].split('/')
    month = int(date[1])
    if month == 12:
        month = 0
    re_map_base[user_id][month] = ''


################ 匿名加工トランザクションデータS から推定mapを作成 ################

##### 各月にどのUserが購入したのかという辞書 s_month_user の枠組みを作る #####
s_month_user = {}
for i in range(0,12):
    s_month_user[i] = []

##### Sから s_month_user の対応月の要素にUser_idを格納していく #####
for item in range(len(S)):
    item_string = (S[item].replace(('\r'or'\n'),'\r\n')).strip()
    item_list = item_string.split(",")
    user_id = item_list[0]
    if user_id == 'DEL':
        continue
    date = item_list[2].split('/')
    month = int(date[1])
    if month == 12:
        month = 0
    s_month_user[month].append(user_id)

##### 推定mapの土台re_map_baseに，月ごとにs_month_userに含まれるUserをランダムに格納する #####
for month in s_month_user:
    count = 0
    user_list = s_month_user[month]
    # 購入Userリストをランダムにシャッフルする
    random.shuffle(user_list)
    for user in re_map_base:
        if re_map_base[user][month] == '':
            count += 1
            if user_list != []:
                #Userリストの先頭から順番に格納
                re_map_base[user][month] = user_list[0]
                # 格納後のUserはリストから消去
                del user_list[0]
            else:
                # 該当月の購入顧客数が，Sの方が少ない場合，DELを格納してしまう
                re_map_base[user][month] = 'DEL'

##### 出力用にフォーマットを整える #####
write_data = []
for user in re_map_base:
    map_row = []
    map_row.append(user)
    map_row.extend(re_map_base[user])
    write_data.append(map_row)


################ 出力 ################
g = open('F_hat.csv', 'w')
writer = csv.writer(g, lineterminator='\n')
writer.writerows(write_data)
g.close()
