"""
File: metrics.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: class for all re-identification metrics
"""

from collections import OrderedDict
import time
import math

import pandas as pd
import numpy as np

from utils import *

class Metrics(object):

    """Docstring for Metrics. """

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonimized: S table, the anonimized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        self._users = M
        self._ground_truth = T
        self._anon_trans = AT
        self._users_t_col = M_col
        self._gt_t_col = T_col
        self._current_score = 0
        self._anonimized = self.generate_S_data()

    def generate_S_data(self):
        """Generate S data from AT data
        :returns: S

        """
        data = self._anon_trans
        data = data.dropna()
        data = data[data[self._gt_t_col['id_user']] != "DEL"]
        #  TODO:check si il y a une seed pour l'aléa  <30-05-18, yourname> #
        data = data.reindex(np.random.permutation(data.index))

        return data


    @property
    def users(self):
        """
        Get the users data
        """
        return self._users

    @property
    def ground_truth(self):
        """
        Get the ground_truth data
        """
        return self._ground_truth

    @property
    def anonimized(self):
        """
        Get the anonimized data
        """
        return self._anonimized

    @property
    def users_t_col(self):
        """
        Get the column used in the M csv
        """
        return self._users_t_col

    @property
    def gt_t_col(self):
        """
        Get the column used in the T csv
        """
        return self._gt_t_col

    @property
    def current_score(self):
        """
        Get the current score calculated by the metrics
        """
        return self._current_score

class ReidentificationMetrics(Metrics):

    """Docstring for S1. """

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonimized: S table, the anonimized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        Metrics.__init__(self, M, T, AT, M_col, T_col)
        self._f_orig = generate_f_orig(self._ground_truth, self._anon_trans, self._gt_t_col)

        #only keep the 2 firsts digit of the id_number (PWSCUP rules)
        #  TODO:Change this rule to keep all digits ?  <31-05-18, Antoine Laurent> #
        self._tronc_product_id(2)


    def _gen_value_id_dic(self, attr):
        """Generate the dictionaty which associate the value ([row[attrs]]) to an id

        :attr: the list of attibutes to check for creating the value
        :return: dictionary of value:id
        """
        value_dic = {}
        for row in self._anonimized.itertuples():
            # Create the value with all the row[attr] concat with ":"
            value = ':'.join([str(row[elt]) for elt in attr])
            value_dic[value] = row[self._gt_t_col['id_user']]
        return value_dic

    def _guess_inialisation(self):
        """Generate a virgin F^ file with DEL on each column for each id

        :return: the dictionary of id:pseudos
        """
        guess = OrderedDict()
        for row in self._users.itertuples():
            # Fill dic[id] with DEL
            guess[row[self._users_t_col['id_user']]] = ['DEL' for i in range(12)]
        return guess

    def _tronc_product_id(self, num):
        """ Tronc the product ID to the number num.
            Example :
                id_prod = ABCDEF and num = 2
                result = AB

        :num: the number of characters to keep.
        """
        col_id_item = self._gt_t_col['id_item']
        self._anonimized.loc[:, col_id_item] = self._anonimized.loc[:, col_id_item]\
                                            .apply(lambda s: s[:min(len(s), num)])
        self._ground_truth.loc[:, col_id_item] = self._ground_truth.loc[:, col_id_item]\
                                            .apply(lambda s: s[:min(len(s), num)])

    def _evaluate(self, attr):
        """ Evaluate the similtude between T and S on attributs attr.

        :attr: attributes to check.
        :return: F^ the guess of Pseudo for each user and each month.
        """

        dic_value_anon = self._gen_value_id_dic(attr)
        guess = self._guess_inialisation()
        for row in self._ground_truth.itertuples():
            #create the concat of the attributes to watch
            value = ':'.join([str(row[i]) for i in attr])
            id_user = row[self._gt_t_col['id_user']]
            if value in dic_value_anon.keys():
                #recover month of the transaction
                month = month_passed(row[self._gt_t_col['date']])
                #affect pseudo for id_user where value == value
                guess[id_user][month] = dic_value_anon[value]

        f_hat = pd.DataFrame(guess).transpose()
        f_hat = f_hat.reset_index()
        f_hat = f_hat.rename(columns={'index':'id_user'})

        return f_hat

    def s1_metrics(self):
        """Calculate metric S1, comparing date and quantity buy on each row.
        Update the current score value

        :returns: the score on this metric (between 0 and 1)

        """
        date_col = self._gt_t_col['date']
        qty_col = self._gt_t_col['qty']

        f_hat = self._evaluate([date_col, qty_col])

        f_hat.to_csv("F_hat.csv", index=False)
        self._f_orig.to_csv("F.csv", index=False)

        score = compare_f_files(self._f_orig, f_hat)
        self._current_score += score

        return score

    def s2_metrics(self):
        """Calculate metric S2, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col['id_item']
        price_col = self._gt_t_col['price']

        f_hat = self._evaluate([id_item_col, price_col])

        score = compare_f_files(self._f_orig, f_hat)
        self._current_score += score

        return score

    def s3_metrics(self):
        """Calculate metric S3, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col['id_item']
        qty_col = self._gt_t_col['qty']

        f_hat = self._evaluate([id_item_col, qty_col])

        score = compare_f_files(self._f_orig, f_hat)
        self._current_score += score

        return score

    def s4_metrics(self):
        """Calculate metric S4, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        date_col = self._gt_t_col['date']
        id_item_col = self._gt_t_col['id_item']

        f_hat = self._evaluate([date_col, id_item_col])

        score = compare_f_files(self._f_orig, f_hat)
        self._current_score += score

        return score

    def s5_metrics(self):
        """Calculate metric S5, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col['id_item']
        price_col = self._gt_t_col['price']
        qty_col = self._gt_t_col['qty']

        f_hat = self._evaluate([id_item_col, price_col, qty_col])

        score = compare_f_files(self._f_orig, f_hat)
        self._current_score += score

        return score

    def s6_metrics(self):
        """Calculate metric S6, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col['id_item']
        date_col = self._gt_t_col['date']
        price_col = self._gt_t_col['price']

        f_hat = self._evaluate([id_item_col, date_col, price_col])

        score = compare_f_files(self._f_orig, f_hat)
        self._current_score += score

        return score

    @property
    def f_orig(self):
        """
        Get the original file F.
        """
        return self._f_orig

class CollaborativeFiltering(object):
    """Docstring for CollaborativeFiltering.

       Return the matrix representing the collaborative filtering on a transactional database.
       It's item x item matrix with c_ij the number of people which have order item_i and item_j.
    """

    def __init__(self, data, tier_for_score, user_threshold, item_table=None, columns=T_COL):
        """
        :data: transaction data on which you want to make the Collaborative filtering
        """
        self._data = data
        self._columns = columns
        if item_table:
            self._item_table = item_table
            self._second_pass = True
        else:
            self._item_table = {}
            self._second_pass = False
        self._user_table = {}
        self._user_item_dic = []
        self._item_user_dic = []
        self._tier_for_score = tier_for_score
        self._user_threshold = user_threshold
        #  TODO: Separer les initialisations des différenttes variables dans des methodes
        #  differentes <05-06-18, Antoine Laurent> #

    def preprocessing_data_cf(self):
        """Process data (T and AT) to generate tables needed for the construction of the similarity
        matrix (or collaborative filtering).

        :return: item_table : table representing all the item, the correspondance between an item
                              and the dictionary item_user_dic
                 user_table : table representing all the user, the correspondance between an item
                              and the dictionary user_item_dic
                 user_item_dic : quantity of item bought by user
                 item_user_dic :
                 total_user_num

        """
        total_user_num = 0
        total_item_num = 0

        if self._second_pass:
            for item_id in self._item_table.keys():
               self._item_user_dic.append({})

        for row in self._data.itertuples():
            user_id = row[self._columns['id_user']]
            item_id = row[self._columns['id_item']]
            quantity = row[self._columns['qty']]

            # Create link between item_user_dic and item table
            if user_id not in self._user_table:
                self._user_table[user_id] = total_user_num
                self._user_item_dic.append({})
                total_user_num += 1

            # We don't want to pass two time in this if it already exist
            if not self._second_pass:
                # Create link between item_user_dic and item table
                if item_id not in self._item_table:
                    self._item_table[item_id] = total_item_num
                    self._item_user_dic.append({})
                    total_item_num += 1

            # Recover link between user_table/item and user_item_dic/item_user_dic
            user_no = self._user_table[user_id]

            # If second_pass then there will possibly have item not contained
            if item_id in self._item_table:
                item_no = self._item_table[item_id]
            else:
                continue

            # Fill item_user_dic
            if user_no not in self._item_user_dic[item_no]:
                self._item_user_dic[item_no][user_no] = quantity
            else:
                self._item_user_dic[item_no][user_no] += quantity

        # In Item-User_dic, convert purchase quantity to score (delete element with score 0)
        for item_no in range(len(self._item_user_dic)):
            for user_no in list(self._item_user_dic[item_no]):
                score = 0
                for elem in range(len(self._tier_for_score)):
                    if self._item_user_dic[item_no][user_no] < self._tier_for_score[elem]:
                        break
                    else:
                        score += 1
                self._item_user_dic[item_no][user_no] = score
                # Delete element with score = 0 (No significant purchase)
                if self._item_user_dic[item_no][user_no] == 0:
                    del self._item_user_dic[item_no][user_no]

        # For each item in the Item-User dictionary,
        # those whose number of users is less than UserNumThr are deleted
        for item_no in range(len(self._item_user_dic)):
            if len(self._item_user_dic[item_no]) < self._user_threshold:
                for user_no in list(self._item_user_dic[item_no]):
                    del self._item_user_dic[item_no][user_no]

        # Fill user_item_dic with item_user_dic
        for item_no in range(len(self._item_user_dic)):
            for user_no, score in self._item_user_dic[item_no].items():
                self._user_item_dic[user_no][item_no] = score

        return (total_user_num, total_item_num, self._user_table, self._item_table,\
                self._user_item_dic, self._item_user_dic)

    def _calc_cos_sim(self, item_no, item2_no):
        """ Calculate the cosinus similarity between items bought by users.

        :item_no: item that as been bought by an user.
        :item2_no: other item bought by the same user at least.

        :return: the cosinus similarity between the vector of people buying item_no and item2_no

        """

        # Initialisation
        cos_sim = 0
        item_vec_size = 0
        item2_vec_size = 0
        inner_product = 0

        for user_no,score in self._item_user_dic[item_no].items():
            # 1つ目のItemの特徴ベクトルのサイズを更新 --> item_vec_size
            item_vec_size += score*score
            # 2つ目のItemの特徴ベクトルにuser_noが含まれていれば，Item同士の内積を更新 --> inner_product
            if user_no in self._item_user_dic[item2_no]:
                score2 = self._item_user_dic[item2_no][user_no]
                inner_product += score*score2
        # Item-User辞書の2つ目のItem No
        for user_no,score2 in self._item_user_dic[item2_no].items():
            # 2つ目のItemの特徴ベクトルのサイズを更新 --> item2_vec_size
            item2_vec_size += score2*score2
        # cosine類似度を計算
        cos_sim = float(inner_product) / float(math.sqrt(item_vec_size) * math.sqrt(item2_vec_size))
        return cos_sim


    def calc_item2item_dic(self):
        """ Calculate the item_item matrix (I(i,j)) from item_user_dic and user_item_dic.
        I(i,j) take the cos_sim distance between i and j.

        :return: the item_item matrix.

        """

        item_item_dic = {}

        # Item-User/User_Item辞書から，denseなところを1に初期化したItem-Item辞書を作成する --> item_item_dic
        for item_no in range(len(self._item_user_dic)):
            for user_no in self._item_user_dic[item_no].keys():
                for item2_no in self._user_item_dic[user_no].keys():
                     if item_no != item2_no:
                        # Item-Item辞書のキー(item_no,item2_no)に対応する値を1に初期化
                        item_item_dic[(item_no,item2_no)] = 1
        # Item-Item辞書のうちdenseなところについて，cosine類似度を求める
        for item_no,item2_no in item_item_dic.keys():
            item_item_dic[(item_no,item2_no)] = self._calc_cos_sim(item_no,item2_no)

        return item_item_dic

    @property
    def data(self):
        """
        Get the data
        """
        return self._data

    @property
    def columns(self):
        """
        Get the columns of the DataFrame data
        """
        return self._columns

    @property
    def item_table(self):
        """
        Get the item_table of the DataFrame data. It's the corespondance between the item_id and
        it's position (item_no).
        """
        return self._item_table

    @property
    def user_table(self):
        """
        Get the user_table of the DataFrame data. It's the corespondance between the user_id and
        it's position (user_no).
        """
        return self._user_table

    @property
    def item_user_dic(self):
        """
        Get the dictionary of item_no->users who've bought the item
        """
        return self._item_user_dic

    @property
    def user_item_dic(self):
        """
        Get the dictionary of user_no->items bought by him
        """
        return self._user_item_dic

    @property
    def tier_for_score(self):
        """
        Get the minimal score possessed by a user to be kept
        """
        return self._tier_for_score

    @property
    def user_threshold(self):
        """
        Get the minimal number of user
        """
        return self._user_threshold

class UtilityMetrics(Metrics):

    """Docstring for UtilityMetrics. """

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonimized: S table, the anonimized version of the _ground_truth (pandas DataFrame)
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        Metrics.__init__(self, M, T, AT, M_col, T_col)


    def _calc_sim_mat_dist(self, item_item_dic1, item_item_dic2):
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

    def e1_metric(self):
        """TODO: Docstring for e1_metric.
        :returns: TODO

        """

        # Processing of Ground Truth Database
        gt_colab_fi = CollaborativeFiltering(self._ground_truth, [12, 24, 36, 48], 1)

        gt_colab_fi.preprocessing_data_cf()
        item_item_dic1 = gt_colab_fi.calc_item2item_dic()

        # Processing of Anonymized Database
        anon_colab_fi = CollaborativeFiltering(self._anonimized, [12, 24, 36, 48], 1,\
                item_table=gt_colab_fi.item_table)

        anon_colab_fi.preprocessing_data_cf()
        item_item_dic2 = anon_colab_fi.calc_item2item_dic()

        # Calcul of the distance
        dist = self._calc_sim_mat_dist(item_item_dic1, item_item_dic2)

        print(dist)
        return dist

def main():
    """main
    """
    start = time.clock()
    T = pd.read_csv('../../data/testing/T.csv', sep=',', engine='c', na_filter=False, low_memory=False)
    T.columns = T_COL.values()
    M = T[T_COL['id_user']].value_counts()
    M = list(M.index)
    M.sort()
    M = pd.DataFrame(M, columns=M_COL.values())
    AT = pd.read_csv('../../data/testing/AT.csv', sep=',', engine='c', na_filter=False, low_memory=False)
    AT.columns = T_COL.values()
    print("Temps de lecture : {}".format(time.clock() - start))


    start = time.clock()
    m = ReidentificationMetrics(M, T, AT)
    print("Temps d'initialisation : {}".format(time.clock() - start))

    start = time.clock()
    print("S1 score : {}".format(m.s1_metrics()))
    print("S2 score : {}".format(m.s2_metrics()))
    print("S3 score : {}".format(m.s3_metrics()))
    print("S4 score : {}".format(m.s4_metrics()))
    print("S5 score : {}".format(m.s5_metrics()))
    print("S6 score : {}".format(m.s6_metrics()))

    print("Temps de calcul : {}".format(time.clock() - start))

    start = time.clock()
    m = UtilityMetrics(M, T, AT)
    print("Temps d'initialisation : {}".format(time.clock() - start))

    start = time.clock()
    print("E1 score : {}".format(m.e1_metric()))

    print("Temps de calcul : {}".format(time.clock() - start))

if __name__ == "__main__":
    main()
