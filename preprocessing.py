import pandas as pd
from utils import T_COL, F_COL, M_COL, PATH_F

"""
File: preprocessing.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: Module made to preprocess the data submitted by darc_evaluator module in the context of
the DARC competition.
"""

def round1_preprocessing(ground_truth_file_path, submission_file_path):
    """Read data for round 1 for Darc Evaluator.
    :returns: all data read.

    """
    # Read the ground truth file
    ground_truth = pd.read_csv(ground_truth_file_path, sep=',', engine='c',\
                               na_filter=False, low_memory=False)
    ground_truth.columns = T_COL.values()

    # Create the dataframe of user in ground truth
    aux_database = ground_truth[T_COL['id_user']].value_counts()
    aux_database = list(aux_database.index)
    aux_database.sort()
    aux_database = pd.DataFrame(aux_database, columns=M_COL.values())

    # Read the submission file
    submission = pd.read_csv(submission_file_path, sep=',', engine='c',\
                             na_filter=False, low_memory=False)
    submission.columns = T_COL.values()

    return ground_truth, aux_database, submission

def round2_preprocessing(submission_file_path, redis_co, attempt_attacked, team_attacked):
    """Read data for round 2 for Darc Evaluator.
    :returns: all data read.

    """
    submission = pd.read_csv(submission_file_path, sep=',', engine='c',\
                             na_filter=False, low_memory=False)
    submission.columns = F_COL

    # Read the ground truth file for this attack
    ground_truth = pd.read_csv("{}/F_{}_attempt_{}.csv".format(PATH_F, team_attacked, attempt_attacked))

    return ground_truth, submission
