"""
File: metrics.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: class for all re-identification metrics
"""

from collections import OrderedDict
import time

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
        pass

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
        Metrics.__init__(self, M, T, M_col, T_col)

def main():
    """main
    """
    start = time.clock()
    T = pd.read_csv('./scripts/usage_example/given_data/T100.csv', sep=',', engine='c', na_filter=False, low_memory=False)
    T.columns = T_COL.values()
    M = T[T_COL['id_user']].value_counts()
    M = list(M.index)
    M.sort()
    M = pd.DataFrame(M, columns=M_COL.values())
    AT = pd.read_csv('./scripts/usage_example/at_data/AT_sample.csv', sep=',', engine='c', na_filter=False, low_memory=False)
    AT.columns = T_COL.values()
    print("Temps de lecture : {}".format(time.clock() - start))


    start = time.clock()
    m = ReidentificationMetrics(M, T, AT)
    print("Temps d'initialisation : {}".format(time.clock() - start))

    start = time.clock()
    print(m.s1_metrics())
    print(m.s2_metrics())
    print(m.s3_metrics())
    print(m.s4_metrics())
    print(m.s5_metrics())
    print(m.s6_metrics())
    print("Temps de calcul : {}".format(time.clock() - start))

if __name__ == "__main__":
    main()
