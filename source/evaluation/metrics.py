"""
File: metrics.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: class for all re-identification metrics
"""

from collections import OrderedDict

M_COL = []
T_COL = []

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

    def _month_passed(date):
        return int(date.split('/')[1]) % 12

    def _sig_gen(S, attr):
        value_dic = {}
        for idx in range(len(S)):
            s = S[idx].strip().split(',')
            value = ':'.join([s[i] for i in range(len(s)) if i in attr])
            value_dic[value] = s[0]
        return value_dic

    def _guess_ini(M):
        guess = OrderedDict()
        for idx in range(len(M)):
            guess[M[idx].strip().split(',')[0]] = ['DEL' for i in range(12)]
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
