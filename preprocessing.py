"""
File: preprocessing.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: Module made to preprocess the data submitted by darc_evaluator module in the context of
the DARC competition.
"""

def round1_preprocessing(ground_truth_file_path, submission_file_path):
    """TODO: Docstring for round1_processing.
    :returns: TODO

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

def round2_preprocessing(submission_file_path, redis_co):
    """TODO: Docstring for round1_processing.
    :returns: TODO

    """

    # Recover the submission number at the end of the filename
    sub_file_name = submission_file_path.split('/')[-1]
    submission_number = sub_file_name.split("_")[-1]
    # Recover opponent team name
    opponent_name = sub_file_name.split("_")[1]

    submission = pd.read_csv(submission_file_path, sep=',', engine='c',\
                             na_filter=False, low_memory=False)
    submission.columns = F_COL

    # Read the ground truth file for this attack
    adress_redis = "F_{}_attempt_{}".format(opponent_name, submission_number)
    ground_truth = pd.read_msgpack(redis_co.get_value(adress_redis))

    if not ground_truth:
        raise Exception("Your attack file name does not match the name standard.")

    return ground_truth, submission, submission_number, opponent_name
