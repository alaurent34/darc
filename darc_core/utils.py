"""
File: utils.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: File containing utilitaries for the DARC competition
"""

import os
import glob

import pandas as pd
import progressbar
import time
# for itertuples which is A LOT faster than iterrows
M_COL = {'id_user':1}
T_COL = {'id_user': 'id_user', 'date': 'date', 'hours': 'hours', 'id_item': 'id_item', 'price': 'price', 'qty': 'qty'}
T_COL_IT = {'id_user':1, 'date':2, 'hours':3, 'id_item':4, 'price':5, 'qty':6}
F_COL = ['id_user', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
NB_GUESS = 3
SIZE_POOL = 7
PATH_F = "./data/f_files/"

# Redis identifiant : do not disclause to participants
# HOST, PORT and PASSWORD have bveen removed from here
# and are instead being picked up as environment variables

def month_passed(date):
    """ Get the month from a date, month should be between 0 and 11

    :date: a date in format YYYY/MM/DD
    :return: integer between 0 and 11 """
    return 0 if date.split('/')[0] == '2010' else int(date.split('/')[1])

def generate_f_orig(ground_truth_trans, anon_trans, gt_t_col=T_COL, gt_t_col_it=T_COL_IT):
    """Generate the F file for the original data, to compare it with the F^ file.

    :returns: F file original

    """

    # Initialization
    f_orig = pd.DataFrame(columns=['id_user', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    f_orig.id_user = ground_truth_trans[gt_t_col['id_user']].value_counts().index
    f_orig = f_orig.sort_values('id_user').reset_index(drop=True)
    f_orig.loc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]] = "DEL"


    seen = set()
    for row in ground_truth_trans.itertuples():
        id_orig = row[gt_t_col_it['id_user']]
        month = month_passed(row[gt_t_col_it['date']])
        id_ano = anon_trans.loc[row[0], gt_t_col['id_user']]
        item = "{}-{}-{}".format(id_orig, month, id_ano)
        if item not in seen and id_ano != "DEL":
            seen.add(item)
            f_orig.loc[f_orig.id_user == id_orig, month] = id_ano

    return f_orig

def compute_all_f_orig(folder_path, ground_truth_file_path):
    """TODO: Docstring for compute_f_orig.

    :folder_path:
    :returns: TODO

    """
    # Read ground truth from csv
    ground_truth = pd.read_csv(ground_truth_file_path, sep=',', engine='c',\
                               na_filter=False, low_memory=False)
    ground_truth.columns = T_COL.values()

    pbar = progressbar.ProgressBar()

    for filepath in pbar(glob.glob(os.path.join(folder_path, 'AT*.csv'))):
        # Read anon data
        at_dataframe = pd.read_csv(filepath, sep=',', engine='c',\
                             na_filter=False, low_memory=False)
        at_dataframe.columns = T_COL.values()

        team_name = filepath.split("/")[-1].split("_")[1]
        attempt = filepath.split("/")[-1].split("_")[2].split(".")[0]

        # Generate F_filepath file
        f_dataframe = generate_f_orig(ground_truth, at_dataframe)

        # Create Dir PATH_F if doesn't exist, otherwise do nothing
        os.makedirs(PATH_F, exist_ok=True)
        # Save F_filepath into PATH_F
        f_dataframe.to_csv("{}/F_{}_attempt_{}.csv".format(PATH_F, team_name, attempt), index=False)



def check_format_trans_file(ground_truth, dataframe):
    """ Check the format of an Anonymized Transaction dataset submitted by a participant. Raise an
    Exception if there is something that does not match the format required.

    :dataframe: The dataframe that represent the participant data.

    :Exception: If there is a problem with the file format.

    """
    #  TODO: Complete the format check if needed otherwise perform some test so we can say "It's all
    #  Good Man !".<19-06-18, Antoine L.> #

    df_copy = dataframe.copy()
    columns = df_copy.columns

    # Check the number of lines of the dataframe
    if df_copy.shape[0] != ground_truth.shape[0]:
        raise Exception(
            "The number of transaction is not the same in the ground_truth and the anonymized file"
        )

    # ID USER should be string before DEL comparision
    try:
        df_copy[columns[0]] = df_copy[columns[0]].apply(lambda x: str(x))
    except Exception:
        raise Exception("Column numero 0 should be of type string")

    # Remove DEL row before value_check
    df_copy = df_copy[df_copy[columns[0]] != 'DEL']

    # Check the number of DEL Row :
    if df_copy.shape[0] < ground_truth.shape[0]/2:
        raise Exception("You cannot suppress more than 50% of the data")

    # Check the number of columns of the DataFrame
    if df_copy.shape[1] != 6:
        raise Exception("Dataset should have 6 columns")

    # Check the columns format : should be string, string, string, string, float, int
    try:
        error_type = []
        for i in range(0, 6):
            if i < 4:
                error_type.append("string")
                df_copy[columns[i]] = df_copy[columns[i]].apply(lambda x: str(x))
            elif i == 5:
                error_type.append("int")
                df_copy[columns[i]] = df_copy[columns[i]].apply(lambda x: int(x))
            else:
                error_type.append("float")
                df_copy[columns[i]] = df_copy[columns[i]].apply(lambda x: float(x))
    except Exception:
        raise Exception("Column numero {} should be of type {}".format(i, error_type[i]))


    # Check that dates stay in the same month
    try:
        gt_dates = pd.to_datetime(
            ground_truth[T_COL['date']], format="%Y/%m/%d"
        ).apply(lambda x: x.month)

        at_dates = pd.to_datetime(
            df_copy[T_COL['date']], format="%Y/%m/%d"
        ).apply(lambda x: x.month)
    except ValueError:
        raise Exception("Date wrong format, should be YYYY/MM/DD")

    if abs(gt_dates - at_dates).max() > 0:
        raise Exception("Date should stay in the same month")

    # Check price value
    if df_copy[T_COL['price']].min() < 0:
        raise Exception("Price should be >= 0 ")

    # Check id products
    gt_products = set(list(ground_truth[T_COL['id_item']]))
    at_products = set(list(df_copy[T_COL['id_item']]))
    if not at_products.issubset(gt_products):
        raise Exception("id_item : ALL id_items should be real")

    # Check number of pseudonyms
    gt_copy = ground_truth.copy()
    df_copy = dataframe.copy()

    gt_copy[T_COL["id_user"]] = gt_copy[T_COL["id_user"]].apply(str)
    df_copy[T_COL["id_user"]] = df_copy[T_COL["id_user"]].apply(str)

    gt_copy = gt_copy[gt_copy[T_COL['id_user']] != "DEL"]
    df_copy = df_copy[df_copy[T_COL['id_user']] != "DEL"]

    gt_copy['month'] = pd.to_datetime(gt_copy[T_COL['date']]).dt.to_period('M')
    gt_copy['id_anon'] = gt_copy[T_COL['id_user']]

    if max(gt_copy.groupby(['month', 'id_user'])['id_anon'].unique().apply(len) > 1):
        raise Exception("You cannot use two pseudonymes for one user ID in one month.")

    # Check for NaN value
    # We don't want to choose a way to interpret a NaN value
    # It should be done by the participant
    size_before = df_copy.shape[0]

    # Remove NaN
    df_copy = df_copy.dropna()
    size_after = df_copy.shape[0]

    if size_before != size_after:
        raise Exception("There should be no NaN value in the data")
    # Check for ':' in id

    # TODO: put time in the logs

    # tps1 = time.clock()
    id_list = df_copy.id_user.unique()
    for id in id_list:
        if ':' in id:
            raise Exception("There should be no \":\" in id")
    # tps2 = time.clock()
    # print("Le code a mis : ",tps2 -tps1, "secondes")

def check_format_f_file(dataframe):
    """ Check the format of a guessed F file submitted by a participant. Raise an
    Exception if there is something that does not match the format requiered.

    :dataframe: The dataframe that represent the participant data.

    :Exception: If there is a problem with the file format.

    """
    # Check for NaN value
    # We don't want to choose a way to interpret a NaN value
    # It should be done by the participant
    columns = dataframe.columns

    # We want str
    dataframe[columns[0]] = dataframe[columns[0]].apply(lambda x: str(x))

    # User_id should not be DEL
    size_before = dataframe.shape[0]

    # Remove NaN
    dataframe = dataframe.dropna()
    size_after = dataframe.shape[0]

    if size_before != size_after:
        raise Exception("There should be no NaN value in the data")
    for row in dataframe.itertuples():
        for i in range(2,15):
            x = row[i].split(':')
            if len(x) > NB_GUESS:
                raise Exception("More guess than allowed")
