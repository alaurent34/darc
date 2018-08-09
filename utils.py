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

# for itertuples which is A LOT faster than iterrows
M_COL = {'id_user':1}
T_COL = {'id_user':1, 'date':2, 'hours':3, 'id_item':4, 'price':5, 'qty':6}
F_COL = ['id_user', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

PATH_F = "./data/f_files/"

# Redis identifiant : do not disclause to participants
HOST = "YourHostHERE"
PORT = 0
PASSWORD = "YourPasswordHERE"

def month_passed(date):
    """ Get the month from a date, month should be between 0 and 11

    :date: a date in format YYYY/MM/DD
    :return: integer between 0 and 11 """
    return int(date.split('/')[1]) % 12

def generate_f_orig(ground_truth_trans, anon_trans, gt_t_col=T_COL):
    """Generate the F file for the original data, to compare it with the F^ file.

    :returns: F file original

    """

    # Initialization
    f_orig = pd.DataFrame(columns=['id_user', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    f_orig.id_user = ground_truth_trans[gt_t_col['id_user']].value_counts().index
    f_orig = f_orig.sort_values('id_user').reset_index(drop=True)
    f_orig.loc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]] = "DEL"


    seen = set()
    for row in ground_truth_trans.itertuples():
        id_orig = row[gt_t_col['id_user']]
        month = month_passed(row[gt_t_col['date']])
        id_ano = anon_trans.loc[row[0], gt_t_col['id_user']]
        item = "{}-{}-{}".format(id_orig, month, id_ano)
        if item not in seen:
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

def compare_f_files(f_orig, f_hat):
    """Compare the two F files to compute the difference and thus the score

    :f: the original f file to compare (pandas DataFrame)
    :f_hat: the guessed f file computed by the metric or adversary (pandas DataFrame)

    :returns: score
    """

    map_error = 0
    score = 0
    count = 0

    #we want the same list of users
    if set(f_orig['id_user']).difference(set(f_hat['id_user'])):
        map_error = 1

    if map_error == 0:
        for row in f_orig.itertuples():
            # Compare each tuple, if they are egual over all month then gain 12 point
            # One points per similarities
            f_ori_tuple = row[1:]
            f_hat_tuple = tuple(f_hat[f_hat['id_user'] == row[1]].iloc[0])
            if f_ori_tuple == f_hat_tuple:
                count += 12
            else:
                for i in range(1,13):
                    if f_ori_tuple[i] == f_hat_tuple[i]:
                        count+=1

    if map_error == 0:
        score += round(float(count)/float(f_orig.shape[0]*12), 6)

    return score

def check_format_trans_file(dataframe):
    """ Check the format of an Anonymized Transaction dataset submitted by a participant. Raise an
    Exception if there is something that does not match the format requiered.

    :dataframe: The dataframe that represent the participant data.

    :Exception: If there is a problem with the file format.

    """
    #  TODO: Complete the format check if needed otherwise perform some test so we can say "It's all
    #  Good Man !".<19-06-18, Antoine L.> #

    # Check the number of columns of the DataFrame
    if dataframe.shape[1] != 6:
        raise Exception("Dataset should have 6 columns")

    # Check the columns format : should be string, string, string, string, float, int
    columns = dataframe.columns
    try:
        error_type = []
        for i in range(0, 6):
            if i < 4:
                error_type.append("string")
                dataframe[columns[i]] = dataframe[columns[i]].apply(lambda x: str(x))
            elif i == 5:
                error_type.append("int")
                dataframe[columns[i]] = dataframe[columns[i]].apply(lambda x: int(x))
            else:
                error_type.append("float")
                dataframe[columns[i]] = dataframe[columns[i]].apply(lambda x: float(x))
    except Exception:
        raise Exception("Column numero {} should be of type {}".format(i, error_type[i]))

    # Check for NaN value
    # We don't want to choose a way to interpret a NaN value
    # It should be done by the participant
    df_copy = dataframe[dataframe[columns[0]] != 'DEL']
    size_before = df_copy.shape[0]

    # Remove NaN
    df_copy = df_copy.dropna()
    size_after = df_copy.shape[0]

    if size_before != size_after:
        raise Exception("There should be no NaN value in the data")

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

    # We want int64
    dataframe[columns[0]] = dataframe[columns[0]].apply(lambda x: int(x))

    # User_id should not be DEL
    size_before = dataframe.shape[0]

    # Remove NaN
    dataframe = dataframe.dropna()
    size_after = dataframe.shape[0]

    if size_before != size_after:
        raise Exception("There should be no NaN value in the data")

