"""
File: metrics.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: class for all re-identification metrics
"""

from collections import OrderedDict

import pandas as pd

#for itertuples which is A LOT faster than iterrows
M_COL = {'id_user':1}
T_COL = {'id_user':1, 'nul':2, 'date':3, 'hours':4, 'id_item':5,\
        'price':6, 'qty':7}

def month_passed(date):
    """ Get the month from a date, month should be between 0 and 11

    :date: a date in format YYYY/MM/DD
    :return: integer between 0 and 11 """
    return int(date.split('/')[1]) % 12o

class Metrics(object):

    """Docstring for Metrics. """

    def __init__(self, M, T, S, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T.
        :_ground_truth: T table containing all transaction of all user for one year.
        :_anonimized: S table, the anonimized version of the _ground_truth
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        self._users = M
        self._ground_truth = T
        self._anonimized = S
        self._users_t_col = M_col
        self._gt_t_col = T_col
        self._current_score = 0

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

    def __init__(self, M, T, S, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T.
        :_ground_truth: T table containing all transaction of all user for one year.
        :_anonimized: S table, the anonimized version of the _ground_truth
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        Metrics.__init__(self, M, T, S, M_col, T_col)


    def _sig_gen(S, attr):
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

    def _guess_ini(M):
        """Generate a virgin F^ file with DEL on each column for each id

        :return: the dictionary of id:pseudos
        """
        guess = OrderedDict()
        for row in self._users.itertuples():
            # Fill dic[id] with DEL
            guess[row[self._users_t_col['id_user']]] = ['DEL' for i in range(12)]
        return guess

    def _drop(S, num):
        """ Tronc the product ID to the number num.
            Example :
                id_prod = ABCDEF and num = 2
                result = AB

        :num: the number of characters to keep.
        """
        for row in self._anonimized.itertuples():
            col_id_item = self._gt_t_col['id_item']
            row[col_id_item] = row[col_id_item][:min(len(row[col_id_item]), num)]

    def _eval(M, T_sub, S):
        """ Evaluate the similtude between T and S on attributs attr.

        :attr: attributes to check.
        :return: F^ the guess of Pseudo for each user and each month.
        """
        #only keep the 2 firsts digit of the id_number
        if self._gt_t_col['id_item'] in attr:
            self._tronc_product_id(2)
        start = time.clock()
        dic_value_anon = self._gen_value_id_dic(attr)
        guess = self._guess_inialisation()
        print("Temps d'initialisation dic : {}".format(time.clock() - start))
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
        return f_hat

class UtilityMetrics(Metrics):

    """Docstring for UtilityMetrics. """

    def __init__(self, M, T, S, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T.
        :_ground_truth: T table containing all transaction of all user for one year.
        :_anonimized: S table, the anonimized version of the _ground_truth
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        Metrics.__init__(self, M, T, S, M_col, T_col)


if __name__ == '__main__':
    M,S,T_sub = common.input(3)
    if 4 in ATTR:       # 4は商品IDについての属性
        S = drop(S, 2)

    common.output([eval(M, T_sub, S)])
