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
        for idx in range(len(S)):
            S_gyo = S[idx].strip().split(',')
            S_gyo[4] = S_gyo[4][0:min(len(S_gyo[4]), num)]
            S[idx] = ','.join(S_gyo)
        return S

    def _eval(M, T_sub, S):
        sig_S = self._sig_gen(S, self.attr)
        guess = self._guess_ini(M)
        for idx in range(len(T_sub)):
            t_sub_gyo = T_sub[idx].strip().split(',')
            value= ':'.join([t_sub_gyo[i] for i in range(len(t_sub_gyo)) if i in self.attr])
            cus_id = t_sub_gyo[0]
            if value in sig_S.keys():
                guess[cus_id][self._month_passed(t_sub_gyo[2])]=sig_S[value]
        return [cus_id+","+",".join(guess[cus_id])  for cus_id in guess.keys()]

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
