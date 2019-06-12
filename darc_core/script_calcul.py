"""
File: script_calcul.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: script to compute manual DARC scores
"""

import pathlib
import sys
import getopt

from multiprocessing import Pool
from functools import partial

from utils import check_format_f_file, check_format_trans_file
from utils import compare_f_files
from preprocessing import round1_preprocessing, round2_preprocessing
from metrics import UtilityMetrics, ReidentificationMetrics

F_PATH = './data/F_files'
S_PATH = './data/S_files'

def metric_wrapper(metric, instance, numero):
    """Launch a metric in function of instance metric and the number of the later.

    :metric: a single char wich is 's' or 'e', respectivly for reid and utility metrics.
    :instance: the instance of a Metric class containing methods `metric`.
    :numero: the ieme method of the instance you want to call.

    :returns: Result of the metric method called.

    """
    method = "{}{}_metric".format(metric, numero)
    return getattr(instance, method)()

def compute_score_round1(ground_truth, aux_database, submission):
    """Compute score for the 1st round of the competition. Score are based on utility metrics
    and Re-identification metrics. The score kept is the max of each category. Score go from 0
    (best) to 1 (worst).

    :ground_truth: DataFrame representing the ground truth data
    :aux_database: DataFrame containing a list of users present in the ground truth
    :submission: DataFrame representing the anonymized transaction database
    :returns: both utility and the f_file

    """
    # Initialize utility metrics
    utility_m = UtilityMetrics(aux_database, ground_truth, submission)

    #Compute utility metrics as subprocesses
    print("Compute Utility metrics")
    metric_pool = Pool()
    utility_wrapper = partial(metric_wrapper, "e", utility_m)
    utility_scores = metric_pool.map(utility_wrapper, range(1, 7))

    # Initialize re-identification metrics
    reid_m = ReidentificationMetrics(aux_database, ground_truth, submission)

    #Compute reidentification metrics as subprocesses
    print("Compute Reidentification metrics")
    metric_pool = Pool()
    reid_wrapper = partial(metric_wrapper, "s", reid_m)
    reid_scores = metric_pool.map(reid_wrapper, range(1, 7))

    # Recover F_orig file
    f_file = reid_m.f_orig
    s_file = reid_m.anonymized

    return utility_scores, reid_scores, f_file, s_file

def compute_score_round2(ground_truth, submission):
    """ Return the re-identification score done by the team submitting on the file anonymized by
    another team.

    It's the score of this team we have to move in the classement.
    :returns: the re-identification score obtained by the anonymized file.

    """
    return compare_f_files(ground_truth, submission)

def arg_help():
    """Print the argument help

    """

    stream = "--ground_truth= \t path to the ground truth file \t\t mandatory\n"\
            +"--submission= \t\t path to the submission file \t\t mandatory\n"\
            +"--round= \t\t the round to execute \t\t\t mandatory"

    return stream

def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    gt_path = ''
    sub_path = ''
    round_nb = None

    try:
        # Short option syntax: "hv:"
        # Long option syntax: "help" or "verbose="
        opts, _ = getopt.getopt(sys.argv[1:], "h", ["help",
                                                    "ground_truth=",
                                                    "submission=",
                                                    "round="])

    except getopt.GetoptError:
        # Print debug info
        print(arg_help())
        sys.exit(1)

    for option, argument in opts:
        if option in ("-h", "--help"):
            print(arg_help())
            sys.exit()
        if option in "--ground_truth":
            gt_path = argument
        if option in "--submission":
            sub_path = argument
        if option in "--round":
            round_nb = int(argument)

    # Check variables
    if gt_path == '' or sub_path == '' or round_nb is None:
        print(arg_help())
        sys.exit(1)

    # Check round
    if round_nb == 1:
        # Read the input files
        ground_truth, aux_database, submission = round1_preprocessing(gt_path, sub_path)
        # Check the format
        check_format_trans_file(ground_truth, submission)
        # Compute scores
        utility_scores, reid_scores, f_file, s_file = compute_score_round1(
            ground_truth,
            aux_database,
            submission
        )
        # Check if F_PATH and S_PATH exist and create it
        pathlib.Path(F_PATH).mkdir(parents=True, exist_ok=True)
        pathlib.Path(S_PATH).mkdir(parents=True, exist_ok=True)

        # Save F file in folder
        f_file.to_csv("{}/F_{}".format(F_PATH, sub_path.split('/')[-1]), index=False)
        #Save S File in folder
        s_file.to_csv("{}/S_{}".format(S_PATH, sub_path.split('/')[-1]), index=False)

        # Print the submission score for round1
        print('')
        print('Utility score :', max(utility_scores))
        print('Re-identificaiton score :', max(reid_scores))

        sys.exit()

    # Else it's round 2
    # Read the input files
    ground_truth = round2_preprocessing(gt_path)
    submission = round2_preprocessing(sub_path)
    # Check the format
    check_format_f_file(submission)

    # Compute round2 score
    reid_score = compute_score_round2(ground_truth, submission)

    #Print the new re-identification score
    print('Re-identification score :', reid_score)

    sys.exit()

if __name__ == "__main__":
    main()
