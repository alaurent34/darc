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

from utils import *
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

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        self._users = M
        self._ground_truth = T
        self._anon_trans = AT
        self._users_t_col = M_col
        self._gt_t_col = T_col
        self._current_score = []
        self._anonymized = self.generate_S_data()

    def generate_S_data(self):
        """Generate S data from AT data.
        :returns: S

        """
        data = self._anon_trans
        # Remove NaN value from DataFrame
        data = data.dropna()
        # Remove 'DEL' row in DataFrame
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

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame).
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        Metrics.__init__(self, M, T, AT, M_col, T_col)
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

    def s1_metric(self):
        """Calculate metric S1, comparing date and quantity buy on each row.
        Update the current score value

        :returns: the score on this metric (between 0 and 1)

        """
        date_col = self._gt_t_col['date']
        qty_col = self._gt_t_col['qty']

        f_hat = self._evaluate([date_col, qty_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s2_metric(self):
        """Calculate metric S2, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col['id_item']
        price_col = self._gt_t_col['price']

        f_hat = self._evaluate([id_item_col, price_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s3_metric(self):
        """Calculate metric S3, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col['id_item']
        qty_col = self._gt_t_col['qty']

        f_hat = self._evaluate([id_item_col, qty_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s4_metric(self):
        """Calculate metric S4, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        date_col = self._gt_t_col['date']
        id_item_col = self._gt_t_col['id_item']

        f_hat = self._evaluate([date_col, id_item_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s5_metric(self):
        """Calculate metric S5, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col['id_item']
        price_col = self._gt_t_col['price']
        qty_col = self._gt_t_col['qty']

        f_hat = self._evaluate([id_item_col, price_col, qty_col])

        score = compare_f_files(self._f_orig, f_hat)
        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def s6_metric(self):
        """Calculate metric S6, comparing date and quantity buy on each row.

        :returns: the score on this metric (between 0 and 1)

        """
        id_item_col = self._gt_t_col['id_item']
        date_col = self._gt_t_col['date']
        price_col = self._gt_t_col['price']

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

class CollaborativeFiltering(object):
    """Docstring for CollaborativeFiltering.

       Return the matrix representing the collaborative filtering on a transactional database.
       It's item x item matrix with c_ij the number of people which have order item_i and item_j.

       Attributes are :
        :data: transaction data on which you want to make the Collaborative filtering
        :columns: name of the columns for data
        :item_table: optional, the precomputed item_table
    """

    def __init__(self, data, item_table=None, columns=T_COL):
        """
        :data: transaction data on which you want to make the Collaborative filtering
        :columns: name of the columns for data
        :item_table: optional, the precomputed item_table
        """
        self._data = data
        self._columns = columns
        if item_table:
            self._item_table = item_table
            self._item_table_exist = True
        else:
            self._item_table = {}
            self._item_table_exist = False
        self._user_table = {}
        self._user_item_dic = []
        self._item_user_dic = []

    def add_user2user_table(self, user_id):
        """ Add an user to the dictionary user_table and an empty entry on in the pair (user, item)
        in user_item_dic

        """
        if user_id not in self._user_table:
            self._user_table[user_id] = len(self._user_table)
            self._user_item_dic.append({})

    def add_item2item_table(self, item_id):
        """ Add an item to the dictionary item_table and an empty entry on in the pair (item, user)
        in item_user_dic

        """
        # Create link between item_user_dic and item table
        if item_id not in self._item_table:
            self._item_table[item_id] = len(self._item_table)
            self._item_user_dic.append({})

    def del_item_cond(self, item_no, user_no):
        """Delete a pair (item, user) in item_user_dic, the condition change depending on the
        attribute max_qty, which is a boolean and mean :
                - True : that we want to delete all users under a given threshold.
                - False : that we want to delete all users above a given threshold.

        """
        # Delete element with score = 0 (Unsignificant purchase for the metric)
        if self._item_user_dic[item_no][user_no] == 0:
            del self._item_user_dic[item_no][user_no]

    def _generate_item_user_dic(self, top_k_ids=None):
        """ Generate a dictionary of pairs (item, user) -> quantity for all the transactions in the
        dataset data.

        If an item_table, which reference all item_id and the position they appear in (and thus
        their position in the list), was passed to at the construction of the object
        CollaborativeFiltering, then we need to skip some part of code.

        :return: item_user_dic with quantity

        """
        if self._item_table_exist:
            for item_id in self._item_table.keys():
               self._item_user_dic.append({})

        for row in self._data.itertuples():
            user_id = row[self._columns['id_user']]
            item_id = row[self._columns['id_item']]
            quantity = row[self._columns['qty']]

            if top_k_ids:
                if item_id not in top_k_ids:
                    continue

            if user_id == 'DEL':
                continue
            # Create link between item_user_dic and item table
            self.add_user2user_table(user_id)

            # We don't want to pass two time in this if it already exist
            if not self._item_table_exist:
                self.add_item2item_table(item_id)

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
                if top_k_ids:
                    self._item_user_dic[item_no][user_no] = 1
            else:
                if top_k_ids:
                    pass
                else:
                    self._item_user_dic[item_no][user_no] += quantity

        return self.item_user_dic

    def _generate_user_item_dic(self):
        """Generate the user_item dictionary with the item_user dictionary.

        Nothing special here

        """
        # Fill user_item_dic with item_user_dic
        for item_no in range(len(self._item_user_dic)):
            for user_no, score in self._item_user_dic[item_no].items():
                self._user_item_dic[user_no][item_no] = score

        return self._user_item_dic

    def _generate_score(self, score_threshold=[12], user_threshold=1, max_qty=True):
        """This method calculate the score to give to a pair (item, user) in function of the
        quantity associated to this pair.

        We can have two case :
            - We want pairs with highter quantity, so we delete pair with quantity < score
              threshold. This case is defined by max_qty = True.
            - We want pairs with lower quantity, so we delete pairs with quantity >= score
              threshold. This case is defined by max_qty = False.

        NB: pairs with less than a user threshold will be deleted too.

        :score_threshold: a list of threshold use to define the score gain by a user. In case of
        max_qty = False, only the lowest item of the list will affect the score.
        :user_threshold: the minimum number of user to have bought the item.
        :max_qty: the information for the quantity threshold.

        :return: the pairs of (item, user) with their score associated.
        """

        # In Item-User_dic, convert purchase quantity to score (delete element with score 0)
        for item_no in range(len(self._item_user_dic)):
            for user_no in list(self._item_user_dic[item_no]):
                score = 0
                for elem in range(len(score_threshold)):
                    if self._item_user_dic[item_no][user_no] < score_threshold[elem]:
                        if max_qty:
                            break
                        else:
                            # Nothing change
                            score = self._item_user_dic[item_no][user_no]
                    else:
                        if max_qty:
                            score += 1
                        else:
                            break
                # Put 0 for item with qty < thrsld or qty > thrsld in regard of the bool max_qty
                self._item_user_dic[item_no][user_no] = score
                # Delete element with depending on quantity
                self.del_item_cond(item_no, user_no)

        # For each item in the Item-User dictionary,
        # those whose number of users is less than UserNumThr are deleted
        for item_no in range(len(self._item_user_dic)):
            if len(self._item_user_dic[item_no]) < user_threshold:
                for user_no in list(self._item_user_dic[item_no]):
                    del self._item_user_dic[item_no][user_no]

        return self._item_user_dic

    def make_topk_item_list(self, k=0):
        """ Determine the top k item list in fonction of the item_table and item_user_dic

            :return: the list of top k items
        """
        # Initialisation
        frequent_item_dic = {}
        top_k_items = []

        # Create a dic with all item and the number of user they bought it
        for tmp_id in range(len(self._item_user_dic)):
            bought_num = 0
            bought_num = len(self._item_user_dic[tmp_id])
            for i, j in self._item_table.items():
                if j == tmp_id:
                    item_id = i
            frequent_item_dic[item_id] = bought_num

        # Sort the dic
        frequent_item_dic = sorted(frequent_item_dic.items(), key=lambda x:(x[1],x[0]), reverse=True)

        # Keep only the k first
        top_k = frequent_item_dic[:k]
        for l in range(len(top_k)):
            top_k_items.append(top_k[l][0])

        return top_k_items

    def preprocessing_data(self, score_threshold=None, user_threshold=None, max_qty_score=True, top_k=False,
                           top_k_ids=None):
        """Process data (T and AT) to generate tables needed for the construction of the similarity
        matrix (or collaborative filtering).

        :return: item_table : table representing all the item, the correspondance between an item
                              and the dictionary item_user_dic
                 user_table : table representing all the user, the correspondance between an item
                              and the dictionary user_item_dic
                 user_item_dic : quantity of item bought by user

        """

        # Generate item_user_dic : item are buyed buy which user by quantity
        self._generate_item_user_dic(top_k_ids=top_k_ids)

        if not top_k:
            # Get scoring done by quantity and with threshold
            self._generate_score(score_threshold, user_threshold, max_qty=max_qty_score)

        self._generate_user_item_dic()

        return (self._user_table, self._item_table, self._user_item_dic,\
                self._item_user_dic)

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
            item_vec_size += score*score

            if user_no in self._item_user_dic[item2_no]:
                score2 = self._item_user_dic[item2_no][user_no]
                inner_product += score*score2

        for user_no,score2 in self._item_user_dic[item2_no].items():
            item2_vec_size += score2*score2

        cos_sim = float(inner_product) / float(math.sqrt(item_vec_size) * math.sqrt(item2_vec_size))
        return cos_sim


    def calc_item2item_dic(self):
        """ Calculate the item_item matrix (I(i,j)) from item_user_dic and user_item_dic.
        I(i,j) take the cos_sim distance between i and j.

        :return: the item_item matrix.

        """
        # Initialization
        item_item_dic = {}

        for item_no in range(len(self._item_user_dic)):
            for user_no in self._item_user_dic[item_no].keys():
                for item2_no in self._user_item_dic[user_no].keys():
                     if item_no != item2_no:
                        item_item_dic[(item_no,item2_no)] = 1

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

    def __init__(self, M, T, AT, M_col=M_COL, T_col=T_COL):
        """
        :_users: M table containing all users present in the transaction data T (pandas DataFrame).
        :_ground_truth: T table containing all transaction of all user for one year (pandas DataFrame).
        :_anonymized: S table, the anonymized version of the _ground_truth (pandas DataFrame)
        :_users_t_col: the name of the columns in the csv file M.
        :_gt_t_col: the name of the columns in the csv file T.
        :_current_score: current score calculated by the metric already processed.
        """
        Metrics.__init__(self, M, T, AT, M_col, T_col)


    def _calc_sim_mat_dist(self, item_item_dic1, item_item_dic2):
        """ Calcul the distance between two item_item matrix.

        return: the distance between the matrix, max value is 1
        """
        sim_dist = 0
        item_item_dic1_sum = 0

        for item_no,item2_no in item_item_dic1:
            item_item_dic1_sum += item_item_dic1[(item_no,item2_no)]

            if (item_no,item2_no) in item_item_dic2:
                sim_dist += math.fabs(item_item_dic1[(item_no,item2_no)] - item_item_dic2[(item_no,item2_no)])
            else:
                sim_dist += item_item_dic1[(item_no,item2_no)]

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
            if self._anon_trans.iloc[idx, self._gt_t_col['id_user']] == "DEL":
                continue

            # Get the date from the data at index idx
            #  TODO: .iloc should be used here for safety reason but iloc does not keep columns
            #  value <12-06-18, Antoine> #
            gt_day = self._ground_truth.loc[idx, self._gt_t_col['date']]
            anon_day = self._anon_trans.loc[idx, self._gt_t_col['date']]

            #  TODO: Mettre ça dans un fichier qui test tous les formats et fait des messages
            #  d'erreurs approprié  <12-06-18, Antoine> #
            try:
                gt_day = pd.datetime.strptime(gt_day, '%Y/%m/%d')
                anon_day = pd.datetime.strptime(anon_day, '%Y/%m/%d')
            except:
                raise Exception("Date wrong format, should be YYYY/MM/DD")

            # Get the difference between date1 and date2 in days
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
            if self._anon_trans.iloc[idx, self._gt_t_col['id_user']] == "DEL":
                continue

            # Get the date from the data at index idx
            gt_price = float(self._ground_truth.loc[idx, self._gt_t_col['price']])
            anon_price = float(self._anon_trans.loc[idx, self._gt_t_col['price']])

            #  TODO: Mettre ça dans un fichier qui test tous les formats et fait des messages
            #  d'erreurs approprié  <12-06-18, Antoine> #
            try:
                if gt_price <= 0 or anon_price < 0:
                    raise Exception("Price should be >= 0 ")
                # Get the difference between date1 and date2 in days
                score += (1 - min(gt_price, anon_price)/max(gt_price, anon_price))
            except:
                raise Exception("Price wrong format")

        score = np.round(float(score)/float(self._anon_trans.shape[0]), 10)

        return score


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

        # Processing of Ground Truth Database
        gt_colab_fi = CollaborativeFiltering(self._ground_truth)

        gt_colab_fi.preprocessing_data([12, 24, 36, 48], 1, max_qty_score=True)
        item_item_dic1 = gt_colab_fi.calc_item2item_dic()

        # Processing of Anonymized Database
        anon_colab_fi = CollaborativeFiltering(self._anon_trans,\
                item_table=gt_colab_fi.item_table)

        anon_colab_fi.preprocessing_data([12, 24, 36, 48], 1, max_qty_score=True)
        item_item_dic2 = anon_colab_fi.calc_item2item_dic()

        # Calcul of the distance
        score = self._calc_sim_mat_dist(item_item_dic1, item_item_dic2)

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

        # Processing of Ground Truth Database
        gt_colab_fi = CollaborativeFiltering(self._ground_truth)

        gt_colab_fi.preprocessing_data([12], 1, max_qty_score=False)
        item_item_dic1 = gt_colab_fi.calc_item2item_dic()

        # Processing of Anonymized Database
        anon_colab_fi = CollaborativeFiltering(self._anon_trans,\
                item_table=gt_colab_fi.item_table)

        anon_colab_fi.preprocessing_data([12], 1, max_qty_score=False)
        item_item_dic2 = anon_colab_fi.calc_item2item_dic()

        # Calcul of the distance
        score = self._calc_sim_mat_dist(item_item_dic1, item_item_dic2)

        # Add the score to the global score for this metric
        self._current_score.append(score)

        return score

    def e3_metric(self, param_k=100):
        """ Caluclate the difference (as in set difference) and similarity matrix between top-`k` items
        bought from ground truth and anonymised dataset.

        :returns: score of the metric.

        """
        # Processing of Ground Truth Database
        ## Creation of Collaborative Filter object
        gt_colab_fi = CollaborativeFiltering(self._ground_truth)

        ## Preprocessing and determination of top k items for GT
        gt_colab_fi.preprocessing_data(max_qty_score=True, top_k=True)
        gt_tok_k_ids = gt_colab_fi.make_topk_item_list(k=param_k)

        #Preprocessing of Anonymized DataBase
        ## Creation of Collaborative Filter object
        anon_colab_fi = CollaborativeFiltering(self._anon_trans,\
                item_table=gt_colab_fi.item_table)

        ## Preprocessing and determination of top k items for AT
        anon_colab_fi.preprocessing_data(max_qty_score=False, top_k=True)
        anon_tok_k_ids = anon_colab_fi.make_topk_item_list(k=param_k)

        # Calcul score for top k items only and retrieve item_table for top k
        gt_colab_fi = CollaborativeFiltering(self._ground_truth)
        gt_colab_fi.preprocessing_data(max_qty_score=True, top_k=True, top_k_ids=gt_tok_k_ids)

        # Obtention of item_item_GT
        item_item_dic1 = gt_colab_fi.calc_item2item_dic()

        # Processing of Anonymized Database for top k item with item_table
        anon_colab_fi = CollaborativeFiltering(self._anon_trans,\
                item_table=gt_colab_fi.item_table)

        anon_colab_fi.preprocessing_data(max_qty_score=True, top_k=True, top_k_ids=gt_tok_k_ids)

        # Obtention of item_item_GT
        item_item_dic2 = anon_colab_fi.calc_item2item_dic()

        # Calcul of the score
        score = []
        score.append(len(set(gt_tok_k_ids).difference(set(anon_tok_k_ids))) / param_k)
        score.append(self._calc_sim_mat_dist(item_item_dic1, item_item_dic2))

        # Add the score to the global score for this metric
        self._current_score.append(max(score))

        return max(score)

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
    AT = pd.read_csv('./data/submission.csv', sep=',', engine='c', na_filter=False, low_memory=False)
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
