"""
File: preprocessing.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description:
"""

import os
import tarfile
import json

import pandas as pd

try:
    from utils import T_COL, F_COL
except ImportError:
    from .utils import T_COL, F_COL


"""
File: preprocessing.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: Module made to preprocess the data submitted by darc_evaluator module in the context of
the DARC competition.
"""

def round1_preprocessing(ground_truth_file_path, submission_file_path=None):
    """Read data for round 1 for Darc Evaluator.
    :returns: all data read.

    """
    # Read the ground truth file
    ground_truth = pd.read_csv(ground_truth_file_path, sep=',', engine='c',\
                               na_filter=False, low_memory=False)
    ground_truth.columns = T_COL.values()

    if submission_file_path:
        # Read the submission file
        submission = pd.read_csv(submission_file_path, sep=',', engine='c',\
                                 na_filter=False, low_memory=False)
        submission.columns = T_COL.values()

        return ground_truth, submission

    return ground_truth

def round2_preprocessing(submission_file_path):
    """Read data for round 2 for Darc Evaluator.
    :returns: all data read.

    """
    submission = pd.read_csv(submission_file_path, sep=',', engine='c',\
                             na_filter=False, low_memory=False)
    submission.columns = F_COL

    return submission

def read_tar(tar_path):
    """Open tar file, recover submission_file_path and infos about the submission in a json file

    :tar_path: path of the tarball
    :returns: submission_file_path, team_attacked, sumbission_id of the file attacked

    """
    # Extract path
    path = '/'.join(tar_path.split('/')[0:-1])

    # Open and extract the tarfile
    tar = tarfile.open(tar_path, "r")
    tar.extractall(path)

    # Recover the path of the submission and informations
    json_path = "crowdai.json"
    for member in tar.members:
        if member.name.split('.')[-1] == 'csv':
            submission_file_path = "{}/{}".format(path, member.name)
        elif member.name.split('.')[-1] == 'json':
            json_path = "{}/{}".format(path, member.name)

    # Open json file
    try:
        json_f = json.load(open(json_path, "r"))
    except FileNotFoundError:
        raise Exception("{} not found in {}".format(json_path, tar_path))

    # Remove json extracted
    os.remove(json_path)

    return submission_file_path, json_f['submission_id_attacked']
