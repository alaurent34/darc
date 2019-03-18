"""
File: metrics.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: class for all re-identification metrics
"""

import sys
from collections import OrderedDict
import time
import math

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import coo_matrix

try:
	from utils import M_COL, T_COL
	from utils import *
except ImportError:
	from .utils import M_COL, T_COL
	from .utils import *

class Metrics(object):

    """Super class Metrics for ReidentificationMetrics and UtilityMetrics. It genreate the S data
    from AT one.

    Attributes are :
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
    """

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL, T_col_it=T_COL_IT):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_gt_t_col: the name of the columns in the csv file T for iteration.
        :_current_score: current score calculated by the metric already processed.
        """
        self._users = M
        self._ground_truth = T
        self._anon_trans = AT
        self._users_t_col = M_col
        self._gt_t_col = T_col
        self._gt_t_col_it = T_col_it
        self._current_score = []

        #  TODO: Cast all data into a fonction  <07-12-18, yourname> #
        self._ground_truth[self._gt_t_col['id_user']] = self._ground_truth[self._gt_t_col['id_user']].apply(str)
        self._anon_trans[self._gt_t_col['id_user']] = self._anon_trans[self._gt_t_col['id_user']].apply(str)

        self._anonymized = self.generate_S_data()

    def generate_S_data(self):
        """Generate S data from AT data.
        :returns: S

        """
        data = self._anon_trans.copy()
        # Remove NaN value from DataFrame
        data = data.dropna()
        # Remove 'DEL' row in DataFrame
        data = data[data[self._gt_t_col['id_user']] != "DEL"]
        #  TODO:check si il y a une seed pour l'aléa  <30-05-18, yourname> #
        data = data.sample(frac=1).reset_index(drop=True)

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
    def anonymized(self):
        """
        Get the anonymized data
        """
        return self._anonymized

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

    """ Reidentification metrics, it create an object that has 6 metrics which calculate the
    pourcentage of reidentification in transaction database, following 6 methods.

    Attributes are :
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
    """

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL, T_col_it=T_COL_IT):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        Metrics.__init__(self, M, T, AT, M_col, T_col, T_col_it)
        self._f_orig = generate_f_orig(self._ground_truth, self._anon_trans, self._gt_t_col)

    def _gen_value_id_dic(self, attrs):
        """Generate the dictionaty which associate the value of the attributes attrs in the
        DataFrame to an user ID.

        :attrs: the list of attibutes to check for creating the value
        :return: dictionary of value:id
        """
        value_dic = {}
        for row in self._anonymized.itertuples():
            # Create the value with all the row[attrs] concat with ":"
            value = ':'.join([str(row[elt]) for elt in attrs])
            value_dic[value] = row[self._gt_t_col_it['id_user']]
        return value_dic

    def _guess_inialisation(self):
        """Generate a virgin F^ file with DEL on each column for each id

        :return: the dictionary of id:pseudos
        """
        guess = OrderedDict()
        for row in self._users.itertuples():
            # Fill dic[id] with DEL
            guess[str(row[self._users_t_col['id_user']])] = ['DEL' for i in range(13)]
        return guess

    def _tronc_product_id(self, num):
        """ Tronc the product ID to the number num.
            Example :
                id_prod = ABCDEF and num = 2
                result = AB

        :num: the number of characters to keep.
        """
        col_id_item = self._gt_t_col['id_item']
        self._anonymized.loc[:, col_id_item] = self._anonymized.loc[:, col_id_item]\
                                            .apply(lambda s: s[:min(len(s), num)])
        self._ground_truth.loc[:, col_id_item] = self._ground_truth.loc[:, col_id_item]\
                                            .apply(lambda s: s[:min(len(s), num)])

    def _evaluate(self, attrs):
        """ Evaluate the similtude between T and S on attributs attrs.

        :attrs: attributes to check.
        :return: F^ the guess of Pseudo for each user and each month.
        """

        dic_value_anon = self._gen_value_id_dic(attrs)
        guess = self._guess_inialisation()
        for row in self._ground_truth.itertuples():
            #create the concat of the attributes to watch
            value = ':'.join([str(row[i]) for i in attrs])
            id_user = row[self._gt_t_col_it['id_user']]
            if value in dic_value_anon.keys():
                #recover month of the transaction
                month = month_passed(row[self._gt_t_col_it['date']])
                #affect pseudo for id_user where value == value
                guess[id_user][month] = dic_value_anon[value]

        f_hat = pd.DataFrame(guess).transpose()
        f_hat = f_hat.reset_index()
        f_hat = f_hat.rename(columns={'index':'id_user'})

        return f_hat

    def s1_metric(self):
        """Calculate metric S1, comparing date and quantity buy on each row.
        Update the current score value

        :returns: the score on this metric (between 0 and 1)

        """
        date_col = self._gt_t_col_it['date']
        qty_col = self._gt_t_col_it['qty']

        f_hat = self._evaluate([date_col, qty_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s2_metric(self):
        """Calculate metric S2, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col_it['id_item']
        price_col = self._gt_t_col_it['price']

        f_hat = self._evaluate([id_item_col, price_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s3_metric(self):
        """Calculate metric S3, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col_it['id_item']
        qty_col = self._gt_t_col_it['qty']

        f_hat = self._evaluate([id_item_col, qty_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s4_metric(self):
        """Calculate metric S4, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        date_col = self._gt_t_col_it['date']
        id_item_col = self._gt_t_col_it['id_item']

        f_hat = self._evaluate([date_col, id_item_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s5_metric(self):
        """Calculate metric S5, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col_it['id_item']
        price_col = self._gt_t_col_it['price']
        qty_col = self._gt_t_col_it['qty']

        f_hat = self._evaluate([id_item_col, price_col, qty_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s6_metric(self):
        """Calculate metric S6, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col_it['id_item']
        date_col = self._gt_t_col_it['date']
        price_col = self._gt_t_col_it['price']

        f_hat = self._evaluate([id_item_col, date_col, price_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    @property
    def f_orig(self):
        """
        Get the original file F.
        """
        return self._f_orig


class UtilityMetrics(Metrics):

    """ Utility metrics, it create an object that has 6 metrics which calculate the
    pourcentage of utility remaining in the anonymized transaction database, following 6 methods.

    Attributes are :
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame)
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
    """

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL, T_col_it=T_COL_IT):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame)
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        Metrics.__init__(self, M, T, AT, M_col, T_col, T_col_it)


    def _calc_sim_mat_dist(self, item_item_dic1, item_item_dic2):
        """ Calcul the distance between two item_item matrix.

        return: the distance between the matrix, max value is 1
        """
        sim_dist = 0
        item_item_dic1_sum = 0

        for item_no, item2_no in item_item_dic1:
            item_item_dic1_sum += item_item_dic1[(item_no, item2_no)]

            if (item_no, item2_no) in item_item_dic2:
                sim_dist += math.fabs(item_item_dic1[(item_no, item2_no)] - item_item_dic2[(item_no, item2_no)])
            else:
                sim_dist += item_item_dic1[(item_no, item2_no)]

        sim_dist /= item_item_dic1_sum

        if sim_dist > 1.0:
            sim_dist = 1.0
        return sim_dist

    def _compare_date_gt_anon(self):
        """Compare each date in T and AT, it's mean to value the transformation applied to the date
        in AT.

        :returns: The total of all the difference between the date in T and AT

        """
        score = 0

        for idx in range(self._anon_trans.shape[0]):
            # Skip this loop if id_user == DEL
            if self._anon_trans.iloc[idx, self._gt_t_col_it['id_user']-1] == "DEL":
                continue

            # Get the date from the data at index idx
            #  TODO: .iloc should be used here for safety reason but iloc does not keep columns
            #  value <12-06-18, Antoine> #
            gt_day = self._ground_truth.loc[idx, self._gt_t_col['date']]
            anon_day = self._anon_trans.loc[idx, self._gt_t_col['date']]

            #  TODO: Mettre ça dans un fichier qui test tous les formats et fait des messages
            #  d'erreurs approprié  <12-06-18, Antoine> #
            gt_day = pd.datetime.strptime(gt_day, '%Y/%m/%d')
            anon_day = pd.datetime.strptime(anon_day, '%Y/%m/%d')

            score += abs((gt_day - anon_day).days)

        score = np.round(float(score)/float(31 * self._anon_trans.shape[0]), 10)

        return score

    def _compare_price_gt_anon(self):
        """Compare each price in T and AT, it's mean to value the transformation applied to the
        price in AT.

        :returns: The total of all the difference between the price in T and AT

        """
        score = 0

        for idx in range(self._anon_trans.shape[0]):
            # Skip this loop if id_user == DEL
            if self._anon_trans.iloc[idx, self._gt_t_col_it['id_user']-1] == "DEL":
                continue

            # Get the date from the data at index idx
            gt_price = float(self._ground_truth.loc[idx, self._gt_t_col['price']])
            anon_price = float(self._anon_trans.loc[idx, self._gt_t_col['price']])

            # Get the difference between date1 and date2 in days
            score += (1 - min(gt_price, anon_price)/max(gt_price, anon_price))

        score = np.round(float(score)/float(self._anon_trans.shape[0]), 10)

        return score

    def compute_median_qty(self):
        """Compute the median of all qty of item buyed

        :return: median of all qty of item buyed
        """
        # Creating item x user sparse matrix for the ground_truth
        gt_id_item_id_user = self.ground_truth.groupby(
            [self._gt_t_col['id_item'], self._gt_t_col['id_user']]
        )[self._gt_t_col['qty']].sum()

        # Recovering median
        median = gt_id_item_id_user.median()

        return median

    def collaborative_filtering_item_user(self, data, e2=False):
        """Compute the matrix of cosine similarity between all items

        :data: dataframe from which to compute the collaborative_filtering
        :returns: matrix |col_item|x|col_item|

        """

        id_items_ori = self.ground_truth[self.gt_t_col["id_item"]].unique()

        # Creating item x user sparse matrix for the ground_truth
        data_id_item_id_user = data.groupby(
            [self._gt_t_col['id_item'], self._gt_t_col['id_user']]
        )[self._gt_t_col['qty']].sum()

        if e2:
            # item x user < median
            data_id_item_id_user = data_id_item_id_user[
                data_id_item_id_user < self.compute_median_qty()
            ]

        # Create dataframe matrix
        data_id_item_id_user = data_id_item_id_user.unstack(level=1).to_sparse()

        items_differ = set(id_items_ori) - set(data_id_item_id_user.index)

        if items_differ:
            df_temp = pd.DataFrame(index=items_differ, columns=data_id_item_id_user.columns)
            data_id_item_id_user = data_id_item_id_user.append(df_temp)

        data_id_item_id_user = data_id_item_id_user.sort_index()

        return cosine_similarity(data_id_item_id_user.fillna(0))

    def e1_metric(self):
        """ Construct a similarity matrix of item buyed (User that have bought this item also bought
        item_i). Here the score is maximized if the quantity is high (calculated by dozen). We
        calculate the difference between the two matrix of item buyed as a score.

        More precisly we construct two matrix M1 and M2, one for the original dataset and one for
        the anonymised one. Both are of size `n x n` where `n` is the number of item. For M_ij
        represent the number of people who have bought the item i and have also bought the item j.

        This procede is called a collaborative filtering
        (https://en.wikipedia.org/wiki/Collaborative_filtering).

        :returns: score of the metric.

        """

        # Copy dataframe
        ground_truth = self._ground_truth.copy()
        anon_trans = self._anon_trans.copy()
        anon_trans = anon_trans.drop(
            anon_trans[anon_trans[self._gt_t_col['id_user']] == 'DEL'].index, axis=0
        ).reset_index(drop=True)

        #  TODO: can be done one time only  <21-12-18, yourname> #
        anon_trans[self._gt_t_col['qty']] = anon_trans[self._gt_t_col['qty']].apply(int)

        # Compute the cosinus similarity item x item
        gt_cos_sim = self.collaborative_filtering_item_user(ground_truth)

        # Compute the cosinus similarity item x item
        at_cos_sim = self.collaborative_filtering_item_user(anon_trans)

        # Compute score
        diff_cos = abs(gt_cos_sim - at_cos_sim)
        score = min(1, diff_cos.sum() / gt_cos_sim.sum())

        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def e2_metric(self):
        """ Construct a similarity matrix of item buyed (User that have bought this item also bought
        item_i). Here the score is maximized if the quantity is low (<= threshold). We
        calculate the difference between the two matrix of item buyed as a score.

        More precisly we construct two matrix M1 and M2, one for the original dataset and one for
        the anonymised one. Both are of size `n x n` where `n` is the number of item. For M_ij
        represent the number of people who have bought the item i and have also bought the item j.

        This procede is called a collaborative filtering
        (https://en.wikipedia.org/wiki/Collaborative_filtering).

        :returns: score of the metric.

        """

        # Copy dataframe
        ground_truth = self._ground_truth.copy()
        anon_trans = self._anon_trans.copy()
        anon_trans = anon_trans.drop(
            anon_trans[anon_trans[self._gt_t_col['id_user']] == 'DEL'].index, axis=0
        ).reset_index(drop=True)

        #  TODO: can be done one time only  <21-12-18, yourname> #
        anon_trans[self._gt_t_col['qty']] = anon_trans[self._gt_t_col['qty']].apply(int)

        # Compute the cosinus similarity item x item
        gt_cos_sim = self.collaborative_filtering_item_user(ground_truth, e2=True)

        # Compute the cosinus similarity item x item
        at_cos_sim = self.collaborative_filtering_item_user(anon_trans, e2=True)

        # Compute score
        diff_cos = abs(gt_cos_sim - at_cos_sim)
        score = min(1, diff_cos.sum() / gt_cos_sim.sum())

        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def e3_metric(self):
        """ Caluclate the difference (as in set difference) and similarity matrix between top-`k`
        items bought from ground truth and anonymised dataset.

        :returns: score of the metric.

        """

        # Copy dataframe
        ground_truth = self._ground_truth.copy()
        anon_trans = self._anon_trans.copy()
        anon_trans = anon_trans.drop(
            anon_trans[anon_trans[self._gt_t_col['id_user']] == 'DEL'].index, axis=0
        ).reset_index(drop=True)

        #  TODO: can be done one time only  <21-12-18, yourname> #
        anon_trans[self._gt_t_col['qty']] = anon_trans[self._gt_t_col['qty']].apply(int)

        # Computing top 5% of most purchased item by customer
        item_count = ground_truth.groupby(self._gt_t_col['id_item']).size()
        gt_top_k = list(
            item_count.sort_values(ascending=False).head(int(item_count.shape[0]*0.05)).index
        )

        # Ground Truth is now with top k items
        ground_truth = ground_truth.set_index(self._gt_t_col['id_item'])
        ground_truth = ground_truth.loc[gt_top_k]
        ground_truth = ground_truth.reset_index()

        # Compute the cosinus similarity item x item
        gt_cos_sim = self.collaborative_filtering_item_user(ground_truth)

        # Computing top 5% of most purchased item by customer
        item_count = anon_trans.groupby(self._gt_t_col['id_item']).size()
        at_top_k = list(
            item_count.sort_values(ascending=False).head(int(item_count.shape[0]*0.05)).index
        )

        # Anonymized File is now with top k items
        anon_trans = anon_trans.set_index(self._gt_t_col['id_item'])
        anon_trans = anon_trans.loc[gt_top_k]
        anon_trans = anon_trans.reset_index()

        # Compute the cosinus similarity item x item
        at_cos_sim = self.collaborative_filtering_item_user(anon_trans)

        # Compute score
        diff_cos = min(1, (abs(gt_cos_sim - at_cos_sim).sum()) / gt_cos_sim.sum())
        # Jaccard distance
        diff_top_k = (
            len(set(gt_top_k).union(at_top_k)) - len(set(gt_top_k).intersection(set(at_top_k)))
        )/ len(set(gt_top_k).union(at_top_k))

        score = max(diff_cos, diff_top_k)

        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def e4_metric(self):
        """ Calculate the mean distance in day between anonymised and ground truth
        transactions.

        :returns: score of the metric.

        """
        score = self._compare_date_gt_anon()
        self._current_score.append(score)

        return score

    def e5_metric(self):
        """ Calculate the difference, as the ratio, of all item prices.

        :returns: score of the metric.

        """
        score = self._compare_price_gt_anon()
        self._current_score.append(score)

        return score

    def e6_metric(self):
        """ Calculate the ratio between the number of lines removed in the anonymized table over the
        number of lines in the original dataset.

        :returns: score of the metric.

        """
        score = np.round(float(1 - self._anonymized.shape[0]/self._ground_truth.shape[0]), 4)
        self._current_score.append(score)

        return score


def main():
    """main
    """
    total_time = time.process_time()
    ######################
    ### Initialisation ###
    ######################

    start = time.process_time()
    T = pd.read_csv('./data/ground_truth.csv', sep=',', engine='c', na_filter=False, low_memory=False)
    T.columns = T_COL.values()
    M = T[T_COL['id_user']].value_counts()
    M = list(M.index)
    M.sort()
    M = pd.DataFrame(M, columns=M_COL.values())
    AT = pd.read_csv('./data/example_files/submission_DEL.csv', sep=',', engine='c', na_filter=False, low_memory=False)
    AT.columns = T_COL.values()
    print("Temps de lecture : {}".format(time.process_time() - start))

    #######################
    ### Utility Metrics ###
    #######################

    start = time.process_time()
    m = UtilityMetrics(M, T, AT)
    print("Temps d'initialisation : {}".format(time.process_time() - start))

    start = time.process_time()
    print("E1 score : {}".format(m.e1_metric()))
    print("E2 score : {}".format(m.e2_metric()))
    print("E3 score : {}".format(m.e3_metric()))
    print("E4 score : {}".format(m.e4_metric()))
    print("E5 score : {}".format(m.e5_metric()))
    print("E6 score : {}".format(m.e6_metric()))

    print("Temps de calcul : {}".format(time.process_time() - start))

    #####################
    ### Re-id Metrics ###
    #####################

    start = time.process_time()
    m = ReidentificationMetrics(M, T, AT)
    print("Temps d'initialisation : {}".format(time.process_time() - start))

    start = time.process_time()
    print("S1 score : {}".format(m.s1_metric()))
    print("S2 score : {}".format(m.s2_metric()))
    print("S3 score : {}".format(m.s3_metric()))
    print("S4 score : {}".format(m.s4_metric()))
    print("S5 score : {}".format(m.s5_metric()))
    print("S6 score : {}".format(m.s6_metric()))

    print("Temps de calcul : {}".format(time.process_time() - start))

    print("Temps de calcul TOTAL : {}".format(time.process_time() - total_time))

    #  TODO: Thread all execution of e* and s* metrics, BUT DO NOT thread utility and Re-id metrics
    #  together because we tronc the item_id in Re-id metrics, and it appears that it's using the
    #  same data due to python not copying value <07-06-18, Antoine Laurent> #

if __name__ == "__main__":
    main()
