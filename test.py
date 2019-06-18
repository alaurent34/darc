"""
Only run this file inside the docker environment, otherwise it will fail

Provide the tested metrics in the file config.py.exemple
Thoose metrics should take the same arguments and return a list of result (for the utility), and
only one float for the reid_metric
"""

# from darc_compare.darc_evaluator import compute_score_round1 as utiliy_metric
# from darc_compare.darc_evaluator import compute_score_round2 as reid_metric
# from config import Config as config
# from utils import T_COL, F_COL, check_format_trans_file

import logging
import glob

from config import Config as config
from darc_core.utils import T_COL, F_COL, check_format_trans_file

from darc_compare.metrics import compute_score_round1 as utiliy_metric

import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity

def check_format_test(ground_truth):
    """TODO: Docstring for check_format_test.
    :returns: TODO

    """
    # Check if the file pass the test, or the tests passed the files
    error = []
    file_err = []
    for file_path in glob.glob(f"{config.TESTING_DIR}/AT/*.csv"):
        sub = pd.read_csv(file_path, names=T_COL.values(), skiprows=1)
        try:
            check_format_trans_file(ground_truth, sub)
        except Exception as err:
            error.append("filename : "+file_path+" : "+str(err))
            file_err.append(file_path)


    if not error:
        logging.info("Format check: No errors")
    else:
        logging.info(f"Format check: Files have poped the folowwing errors : \n {error}")

    return file_err

def test_reid_scoring():
    """TODO: Docstring for test_k_guess_scoring.
    :returns: TODO

    """
    ground_truth = pd.read_csv(f"{config.GROUND_TRUTH}")
    at_file = pd.read_csv(f"{config.TESTING_DIR}/AT/dabe15b958bcb0967c968d035f9148d9.csv")
    scores = pd.DataFrame(
        columns=range(1, 7),
        index=glob.glob(f"{config.TESTING_DIR}/F/*.csv")
        )

    metric = config.metric_class(ground_truth, at_file)
    for file_path in glob.glob(f"{config.TESTING_DIR}/F/*.csv"):
        sub = pd.read_csv(file_path, names=F_COL, skiprows=1)

        scores.loc[file_path] = metric.compare_f_files(sub)

    return scores


def oracle_test(ground_truth, aux, file_err):
    """ Compare results obtained by original DARC and new version proposed
    :returns: A file containing the differences

    """
    scores_oracle = pd.DataFrame(
        columns=range(1, 13),
        index=glob.glob(f"{config.TESTING_DIR}/AT/*.csv")
        )
    scores_new = pd.DataFrame(
        columns=range(1, 13),
        index=glob.glob(f"{config.TESTING_DIR}/AT/*.csv")
        )

    # We want to compare if two way of doing the metrics change something on the results
    for file_path in glob.glob(f"{config.TESTING_DIR}/AT/*.csv"):
        if file_path in file_err:
            scores_oracle.drop(file_path, inplace=True)
            scores_new.drop(file_path, inplace=True)
            continue
        try:
            sub = pd.read_csv(file_path, names=T_COL.values(), skiprows=1)

            utility_scores, reid_scores, _, _ = utiliy_metric(ground_truth, aux, sub)
            scores_oracle.loc[file_path] = utility_scores + reid_scores

            metrics = config.metric_class(ground_truth, sub)
            scores_new.loc[file_path] = metrics.scores()
        except Exception as err:
            scores_oracle.drop(file_path, inplace=True)
            scores_new.drop(file_path, inplace=True)
            logging.info(f"{file_path} encoutred the following error : {err}")

    return scores_oracle, scores_new

def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    logging.basicConfig(filename=f'/test/{config.TESTING_DIR}/testing.log', level=logging.DEBUG)

    ground_truth = pd.read_csv(
        config.GROUND_TRUTH, names=T_COL.values(), low_memory=False, skiprows=1
        )
    aux = pd.DataFrame(ground_truth.id_user.drop_duplicates().sort_values(), columns=["id_user"]).reset_index(drop=True)

    logging.info("================ START NEW TESTS =================")
    logging.info("---------------: Computation :----------------")
    logging.info("Check Format ...")
    file_err = check_format_test(ground_truth)
    logging.info("Done")
    logging.info("Compare new version with tested one")
    scores_oracle, scores_new = oracle_test(ground_truth, aux, file_err)
    logging.info("Done")
    logging.info("Run reid on sample of F_files")
    scores_reid = test_reid_scoring()
    logging.info("Done")

    logging.info("---------------: RESULTS :----------------")
    logging.info(f"Cosine Similarity between files : {cosine_similarity(scores_oracle, scores_new)}")
    #  TODO: Normalize ?  <11-06-19, yourname> #
    logging.info(f"Substraction : \n {(scores_oracle - scores_new).sum(axis=1).to_string()}")

    # All values <=1 ?
    logging.info("---------------: Values in [0, 1] ? :---------------")
    bool_oracle = (scores_oracle <= 1).all().all() and (scores_oracle >= 0).all().all()
    logging.info(f"Scores Oracle : {bool_oracle}")
    if not bool_oracle:
        logging.info(f"{scores_oracle.to_string()}")

    bool_new = (scores_new <= 1).all().all() and (scores_new >= 0).all().all()
    logging.info(f"Scores new method : {bool_new}")
    if not bool_new:
        logging.info(f"{scores_new.to_string()}")

    bool_reid = (scores_reid <= 1).all().all() and (scores_reid >= 0).all().all()
    logging.info(f"Scores reid : {bool_reid}")
    if not bool_reid:
        logging.info(f"{scores_reid.to_string()}")

    logging.info("---------------: Reid Scores :---------------")
    logging.info(f"\n{scores_reid.to_string()}")

if __name__ == "__main__":
    main()
