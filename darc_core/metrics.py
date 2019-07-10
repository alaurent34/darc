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
from multiprocessing import Pool
from pathos.multiprocessing import ProcessingPool as PPool
from functools import partial

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import coo_matrix

try:
    from utils import M_COL, T_COL, T_COL_IT, NB_GUESS, SIZE_POOL
except ImportError:
    from .utils import M_COL, T_COL, T_COL_IT, NB_GUESS, SIZE_POOL

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

    def __init__(self, T, AT, M_col=M_COL, T_col=T_COL, T_col_it=T_COL_IT):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_gt_t_col: the name of the columns in the csv file T for iteration.
        :_current_score: current score calculated by the metric already processed.
        """
        self._ground_truth = T
        self._users = pd.DataFrame(self._ground_truth.id_user.drop_duplicates().sort_values(), columns=["id_user"]).reset_index(drop=True)
        self._anon_trans = AT
        self._users_t_col = M_col
        self._gt_t_col = T_col
        self._gt_t_col_it = T_col_it
        self._current_score = []

        #  TODO: Cast all data into a fonction  <07-12-18, yourname> #
        self._ground_truth[self._gt_t_col['id_user']] = self._ground_truth[self._gt_t_col['id_user']].apply(str)
        self._anon_trans[self._gt_t_col['id_user']] = self._anon_trans[self._gt_t_col['id_user']].apply(str)

        self._anonymized = self.generate_S_data()

        self._f_orig = self.f_orig()


    def scores_util(self):
        return [self._e1_metric(), self._e2_metric(), self._e3_metric(), self._e4_metric(), self._e5_metric(), self._e6_metric()]

    def scores_reid(self):
        return [self._s1_metric(), self._s2_metric(), self._s3_metric(), self._s4_metric(), self._s5_metric(), self._s6_metric(), self._s7_metric()]

    def scores(self):
        return self.scores_util() + self.scores_reid()

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

    def month_passed(self, date):
        """ Get the month from a date, month should be between 0 and 11

        :date: a date in format YYYY/MM/DD
        :return: integer between 0 and 11 """
        return 0 if date.split('/')[0] == '2010' else int(date.split('/')[1])

    def f_orig(self):
        """Generate the F file for the original data, to compare it with the F^ file.

        :returns: F file original

        """

        # Initialization
        f_orig = pd.DataFrame(columns=['id_user', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        f_orig.id_user = self._ground_truth[self._gt_t_col['id_user']].value_counts().index
        f_orig = f_orig.sort_values('id_user').reset_index(drop=True)
        f_orig.loc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]] = "DEL"


        seen = set()
        for row in self._ground_truth.itertuples():
            id_orig = row[self._gt_t_col_it['id_user']]
            month = self.month_passed(row[self._gt_t_col_it['date']])
            id_ano = self._anon_trans.loc[row[0], self._gt_t_col['id_user']]
            item = "{}-{}-{}".format(id_orig, month, id_ano)
            if item not in seen and id_ano != "DEL":
                seen.add(item)
                f_orig.loc[f_orig.id_user == id_orig, month] = id_ano

        return f_orig

    def compare_f_files(self, f_hat):
        """Compare the two F files to compute the difference and thus the score

        :f: the original f file to compare (pandas DataFrame)
        :f_hat: the guessed f file computed by the metric or adversary (pandas DataFrame)

        :returns: score
        """

        #tps1 = time.clock()
        map_error = 0
        score = 0
        count = 0
        total = 0

        #we want the same list of users
        if set(self._f_orig['id_user']).difference(set(f_hat['id_user'])):
            map_error = 1

        if map_error == 0:
            for row in self._f_orig.itertuples():
                # Compare each tuple, if they are egual over all month then gain 12 points
                # One points per similarities
                f_ori_tuple = row[1:]
                f_hat_tuple = tuple(f_hat[f_hat['id_user'] == row[1]].iloc[0])
                for i in range(1, 13):
                    if f_ori_tuple[i] != "DEL":
                        total += 1
                        count += self._compare_row_f_file(f_ori_tuple[i], f_hat_tuple[i])
        #            if f_ori_tuple[i] == f_hat_tuple[i] and f_ori_tuple[i] != "DEL":
        #                count += 1


        if map_error == 0:
            score += round(float(count)/float(total), 6)

        return score

    def _compare_row_f_file(self, row_orig, row_sub):
        """
        Check if row_orig is a substring of row_sub, i.e did the participant submit
        the good id among all id submitted
        """
        row_sub = row_sub.split(':')
        count = 0
        for i in range(len(row_sub)):
            if row_orig in row_sub[i]:
                count = (NB_GUESS - i)/NB_GUESS
        return count

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
                month = self.month_passed(row[self._gt_t_col_it['date']])
                #affect pseudo for id_user where value == value
                guess[id_user][month] = dic_value_anon[value]

        f_hat = pd.DataFrame(guess).transpose()
        f_hat = f_hat.reset_index()
        f_hat = f_hat.rename(columns={'index':'id_user'})

        return f_hat

    def _subset(self, month):
        """
        TODO
        """
        subset1 = time.clock()
        # On définit le masque en fonction du mois, beacoup de cas -> le code est dégeu
        if month != 0 :
            if month < 9:
                start = '2011-0'+str(month)+'-01'
                end = '2011-0'+str(month+1) +'-01'
            if month == 9:
                start = '2011-0'+str(month)+'-01'
                end = '2011-10-01'
            if month == 12:
                start = '2011-'+str(month)+'-01'
                end = '2012-01-01'
            else:
                start = '2011-'+str(month)+'-01'
                end = '2011-'+str(month+1) +'-01'
        else:
            start = '2010-12-01'
            end = '2010-12-31'
        self._ground_truth['date'] = pd.to_datetime(self._ground_truth['date'])
        mask1 = (self._ground_truth['date'] >= start) & (self._ground_truth['date'] < end)
        self._anonymized['date'] = pd.to_datetime(self._anonymized['date'])
        mask2 = (self._anonymized['date'] >= start) & (self._anonymized['date'] < end)

        t_month=self._ground_truth.loc[mask1]
        a_month=self._anonymized.loc[mask2]

        subset2 = time.clock()
        return t_month, a_month, month

    @staticmethod
    def _compute_score(a, t):
        """
        TODO : Find a way to put it in a lambda
        """
        return len(a.intersection(t))/len(t)

    def _find_k_guess(self, t_month, a_month, month):
        """
        TODO
        """
        #k_guess1 = time.clock()

        #Fabrication du vecteur d'item pour chaque utilisateur
        t_month_group=t_month.groupby('id_user')['id_item'].apply(set)
        a_month_group=a_month.groupby('id_user')['id_item'].apply(set)

        # Début du calculs des coefficients de similiarité.
        d_month=dict()
        d_month['month'] = month

        for id_t in t_month_group.index:
            list_guess = list()
            guess = str()
            inter_a_t = a_month_group.apply( lambda x : self._compute_score(x, t_month_group.loc[id_t]))
            top_guess = inter_a_t.nlargest(NB_GUESS)
            for index in top_guess.index :
                 guess += str(index) + ':'
            d_month[id_t] = guess[:-1]
        #k_guess2 = time.clock()
        return d_month

    def _s1_metric(self):
        """Calculate metric S1, comparing date and quantity buy on each row.
        Update the current score value

        :returns: the score on this metric (between 0 and 1)

        """
        date_col = self._gt_t_col_it['date']
        qty_col = self._gt_t_col_it['qty']

        f_hat = self._evaluate([date_col, qty_col])

        score = self.compare_f_files(f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def _s2_metric(self):
        """Calculate metric S2, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col_it['id_item']
        price_col = self._gt_t_col_it['price']

        f_hat = self._evaluate([id_item_col, price_col])

        score = self.compare_f_files(f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def _s3_metric(self):
        """Calculate metric S3, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col_it['id_item']
        qty_col = self._gt_t_col_it['qty']

        f_hat = self._evaluate([id_item_col, qty_col])

        score = self.compare_f_files(f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def _s4_metric(self):
        """Calculate metric S4, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        date_col = self._gt_t_col_it['date']
        id_item_col = self._gt_t_col_it['id_item']

        f_hat = self._evaluate([date_col, id_item_col])

        score = self.compare_f_files(f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def _s5_metric(self):
        """Calculate metric S5, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col_it['id_item']
        price_col = self._gt_t_col_it['price']
        qty_col = self._gt_t_col_it['qty']

        f_hat = self._evaluate([id_item_col, price_col, qty_col])

        score = self.compare_f_files(f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def _s6_metric(self):
        """Calculate metric S6, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col_it['id_item']
        date_col = self._gt_t_col_it['date']
        price_col = self._gt_t_col_it['price']

        f_hat = self._evaluate([id_item_col, date_col, price_col])

        score = self.compare_f_files(f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def _s7_metric(self):
        """
        TODO
        """
        def _reid_multi(month):
            return self._find_k_guess(*self._subset(month))

        Df_list = list()
        F_list = list()
        with PPool(SIZE_POOL) as p:
            F_list = p.map( _reid_multi, [i for i in range(13)])
        F_list = sorted(F_list, key=lambda x : x['month'], reverse = False)
        dtypes = {'id_user': str}
        user_id = pd.DataFrame(sorted(self._ground_truth["id_user"].unique()))
        user_id.columns = ['id_user']
        user_id = user_id.set_index('id_user')
        Df_list.append(user_id)
        for dict_month in F_list:
            col = dict_month.pop("month")
            df = pd.DataFrame.from_dict(dict_month, orient='index')
            df.columns = [col]
            Df_list.append(df)
        F_file = pd.concat(Df_list, axis=1, join_axes=[Df_list[0].index])
        F_file = F_file.reset_index()
        F_file = F_file.fillna('DEL')

        score = self.compare_f_files(F_file)
        self._current_score.append(score)

        return score

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

    def _compute_median_qty(self):
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

    def _collaborative_filtering_item_user(self, data, e2=False):
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
                data_id_item_id_user < self._compute_median_qty()
            ]

        # Create dataframe matrix
        data_id_item_id_user = data_id_item_id_user.unstack(level=1).to_sparse()

        items_differ = set(id_items_ori) - set(data_id_item_id_user.index)

        if items_differ:
            df_temp = pd.DataFrame(index=items_differ, columns=data_id_item_id_user.columns)
            data_id_item_id_user = data_id_item_id_user.append(df_temp)

        data_id_item_id_user = data_id_item_id_user.sort_index()

        return cosine_similarity(data_id_item_id_user.fillna(0))

    def _e1_metric(self):
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
        gt_cos_sim = self._collaborative_filtering_item_user(ground_truth)

        # Compute the cosinus similarity item x item
        at_cos_sim = self._collaborative_filtering_item_user(anon_trans)

        # Compute score
        diff_cos = abs(gt_cos_sim - at_cos_sim)
        score = min(1, diff_cos.sum() / gt_cos_sim.sum())

        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def _e2_metric(self):
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

        if True:
            return 0

        # Copy dataframe
        ground_truth = self._ground_truth.copy()
        anon_trans = self._anon_trans.copy()
        anon_trans = anon_trans.drop(
            anon_trans[anon_trans[self._gt_t_col['id_user']] == 'DEL'].index, axis=0
        ).reset_index(drop=True)

        #  TODO: can be done one time only  <21-12-18, yourname> #
        anon_trans[self._gt_t_col['qty']] = anon_trans[self._gt_t_col['qty']].apply(int)

        # Compute the cosinus similarity item x item
        gt_cos_sim = self._collaborative_filtering_item_user(ground_truth, e2=True)

        # Compute the cosinus similarity item x item
        at_cos_sim = self._collaborative_filtering_item_user(anon_trans, e2=True)

        # Compute score
        diff_cos = abs(gt_cos_sim - at_cos_sim)
        score = min(1, diff_cos.sum() / gt_cos_sim.sum())

        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def _e3_metric(self):
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
        gt_cos_sim = self._collaborative_filtering_item_user(ground_truth)

        # Computing top 5% of most purchased item by customer
        item_count = anon_trans.groupby(self._gt_t_col['id_item']).size()
        at_top_k = list(
            item_count.sort_values(ascending=False).head(int(item_count.shape[0]*0.05)).index
        )

        # Anonymized File is now with top k items
        anon_trans = anon_trans.set_index(self._gt_t_col['id_item'])
        anon_trans = anon_trans.loc[at_top_k]
        anon_trans = anon_trans.reset_index()

        # Compute the cosinus similarity item x item
        at_cos_sim = self._collaborative_filtering_item_user(anon_trans)

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

    def _e4_metric(self):
        """ Calculate the mean distance in day between anonymised and ground truth
        transactions.

        :returns: score of the metric.

        """
        score = self._compare_date_gt_anon()
        self._current_score.append(score)

        return score

    def _e5_metric(self):
        """ Calculate the difference, as the ratio, of all item prices.

        :returns: score of the metric.

        """
        score = self._compare_price_gt_anon()
        self._current_score.append(score)

        return score

    def _e6_metric(self):
        """ Calculate the ratio between the number of lines removed in the anonymized table over the
        number of lines in the original dataset.

        :returns: score of the metric.

        """
        score = np.round(float(1 - self._anonymized.shape[0]/self._ground_truth.shape[0]), 4)
        self._current_score.append(score)

        return score

    @property
    def f(self):
        """
        Get the original file F.
        """
        return self._f_orig


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

def metric_wrapper(metric, instance, numero):
    """Launch a metric in function of instance metric and the number of the later.

    :metric: a single char wich is 's' or 'e', respectivly for reid and utility metrics.
    :instance: the instance of a Metric class containing methods `metric`.
    :numero: the ieme method of the instance you want to call.

    :returns: Result of the metric method called.

    """
    method = "_{}{}_metric".format(metric, numero)
    return getattr(instance, method)()

def utility_metric(ground_truth, sub):
    """TODO: Docstring for utility_metric.

    :arg1: TODO
    :returns: TODO

    """
    # Initialize utility metrics
    metric = Metrics(ground_truth, sub)

    #Compute utility metrics as subprocesses
    metric_pool = Pool()
    utility_wrapper = partial(metric_wrapper, "e", metric)
    utility_scores = metric_pool.map(utility_wrapper, range(1, 7))

    #Compute reidentification metrics as subprocesses
    metric_pool = Pool()
    reid_wrapper = partial(metric_wrapper, "s", metric)
    reid_scores = metric_pool.map(reid_wrapper, range(1, 8))

    return utility_scores + reid_scores
