import os
import os.path
import pickle
import time
import shutil
import glob

import pandas as pd
import numpy as np

from utils import *
import metrics

class DarcEvaluator:
    """
    Evaluate submission file of users in the context od DARC competition
    This is a fork from crowdai_evaluator https://github.com/crowdAI/crowdai-example-evaluator
    """
    def __init__(self, answer_file_path, round=1):
        """
        `round` : Holds the round for which the evaluation is being done.
        can be 1, 2...upto the number of rounds the challenge has.
        Different rounds will mostly have different ground truth files.
        """
        self.answer_file_path = answer_file_path
        self.round = round

    def evaluate(self, client_payload, _context={}):
        """
        `client_payload` will be a dict with (atleast) the following keys :
          - submission_file_path : local file path of the submitted file
        """

        # Initialize the score variables, 2nd one is just use for the first round
        primary_score = None
        secondary_score = None

        # Initialize directory variable
        team = _context['team_name']
        team_directory = "./data/teams/{}/".format(team)
        f_directory = "./data/teams/F_files/"
        anon_name = client_payload['anon_name']
        current_milli_time = int(round(time.time() * 1000))
        # Determine the score depending on the round

        ## ROUND 1
        if self.round == 1:
            # Read the ground truth file
            ground_truth = pd.read_csv(self.answer_file_path, sep=',', engine='c',\
                                       na_filter=False, low_memory=False)
            ground_truth.columns = T_COL.values()

            # Create the dataframe of user in ground truth
            aux_database = ground_truth[T_COL['id_user']].value_counts()
            aux_database = list(aux_database.index)
            aux_database.sort()
            aux_database = pd.DataFrame(aux_database, columns=M_COL.values())

            # Read the submission file
            submission_file_path = client_payload["submission_file_path"]
            submission = pd.read_csv(submission_file_path, sep=',', engine='c',\
                                     na_filter=False, low_memory=False)
            submission.columns = T_COL.values()

            # Check the format of the Anonymized Transaction file
            check_format_trans_file(submission)

            # Determine all the scores for a anonymization transaction file
            utility_scores, reid_scores, f_file, s_file = self._round1(ground_truth, aux_database,\
                                                               submission)

            # Create the team folder if not already existing
            if not os.path.exists(team_directory):
                os.makedirs(team_directory)

            # Create the folder for the anonymisation file submit and score get
            if not os.path.exists(team_directory+"{}_{}".format(anon_name, current_milli_time)):
                os.makedirs(team_directory+"{}_{}".format(anon_name, current_milli_time))

            # Create folder containing F_files of every teams (used for re-identification)
            if not os.path.exists(f_directory):
                os.makedirs(f_directory)

            # Save the AT file for the current team
            submission.to_csv("{}/{}_{}/AT.csv"\
                      .format(team_directory, anon_name, current_milli_time), index=False)
            # Save S file for the current team
            s_file.to_csv("{}/{}_{}/S_{}_{}_{}.csv"\
                      .format(team_directory, anon_name, current_milli_time,\
                              team, anon_name, current_milli_time), index=False)
            # Save the F file for the current team
            f_file.to_csv(f_directory+"/F_{}_{}_{}.csv"\
                  .format(team, anon_name, current_milli_time), index=False)

            # Display to the player his scores on all metrics
            for i in range(len(utility_scores)):
                print("E{} : {}".format(i, utility_scores[i]))
            for i in range(len(reid_scores)):
                print("S{} : {}".format(i, reid_scores[i]))

            primary_score = max(utility_scores)
            secondary_score = max(reid_scores)

            # Save the best score for each team
            with open("{}/{}_{}/scores.txt".format(team_directory, anon_name, current_milli_time), "w+") as score_file:
                score_file.write("Utility score : {}\n".format(primary_score))
                score_file.write("Re-identification score : {}".format(secondary_score))

            # Count the number of directories inside team folder
            nb_dir = len([name for name in os.listdir(team_directory) if os.path.isdir(team_directory+name)])

            # Keep only 3 latest attempts
            if nb_dir > 3:
                # Work only if we never change dir after creating
                oldest_dir = min(glob.iglob(team_directory+"/*"), key=os.path.getctime)

                # Check if the selected dir is really the oldest
                for dir_name in os.listdir(team_directory):
                    if dir_name.split('_')[-1] < oldest_dir.split('_')[-1]:
                        oldest_dir = team_directory+dir_name

                infos = '_'.join(oldest_dir.split('/')[-1].split('_')[-2:])

                # Remove the oldest attempt
                shutil.rmtree(oldest_dir, ignore_errors=False)
                os.remove(f_directory+"/F_{}_{}.csv".format(team, infos))

        # ROUND 2
        elif self.round == 2:

            # Initialisation of parameters
            submission_file_path = client_payload["submission_file_path"]

            sub_file_name = submission_file_path.split('/')[-1]
            infos = "_".join(sub_file_name.split("_")[1:])

            submission = pd.read_csv(submission_file_path, sep=',', engine='c',\
                                     na_filter=False, low_memory=False)
            submission.columns = F_COL

            # Read the ground truth file for this attack
            try:
                ground_truth = pd.read_csv("./data/teams/F_files/F_{}.csv".format(infos))
            except Exception:
                raise Exception("Your attack file name does not match the name standard")

            #######################################
            ####### Limit the nb of attemps #######
            #######################################

            # Create the rep to save the attemps for each team
            if not os.path.exists("./data/teams/aux/"):
                os.makedirs("./data/teams/aux/")

            try:
                with open("./data/teams/aux/{}_vs_{}".format(team, sub_file_name), "rb") as file_nb_atcks:
                    nb_atcks = pickle.load(file_nb_atcks)
            except FileNotFoundError:
                nb_atcks = 0

            # Check if they've attacked them 10 times already
            if nb_atcks >= 10:
                raise Exception("You've reach your 10 attempts on this file.")

            check_format_f_file(submission)
            score_reid = self._round2(ground_truth, submission)

            primary_score = score_reid

            nb_atcks +=1
            with open("./data/teams/aux/{}_vs_{}".format(team, sub_file_name), "wb") as file_nb_atcks:
                pickle.dump(nb_atcks, file_nb_atcks)

        # Return object
        _result_object = {
            "primary_score": primary_score,
            "secondary_score" : secondary_score
            }

        return _result_object

    def _round1(self, ground_truth, aux_database, submission):
        """Compute score for the 1st round of the competition. Score are based on utility metrics
        and Re-identification metrics. The score kept is the max of each category. Score go from 0
        (best) to 1 (worst).

        :ground_truth: DataFrame representing the ground truth data
        :aux_database: DataFrame containing a list of users present in the ground truth
        :submission: DataFrame representing the anonymized transaction database
        :returns: both utility and the f_file

        """
        # Initialize utility metrics
        utility_m = metrics.UtilityMetrics(aux_database, ground_truth, submission)

        print("Compute Utility metrics")
        # Compute all the utility metrics
        utility_m.e1_metric()
        utility_m.e2_metric()
        utility_m.e3_metric()
        utility_m.e4_metric()
        utility_m.e5_metric()
        utility_m.e6_metric()

        # Recover the utility scores
        utility_scores = utility_m.current_score

        # Initialize re-identification metrics
        reid_m = metrics.ReidentificationMetrics(aux_database, ground_truth, submission)

        print("Compute Re-identification metrics")
        # Compute all the re-identificaiton metrics
        reid_m.s1_metrics()
        reid_m.s2_metrics()
        reid_m.s3_metrics()
        reid_m.s4_metrics()
        reid_m.s5_metrics()
        reid_m.s6_metrics()

        # Recover the re-identification scores
        reid_scores = reid_m.current_score

        # Recover F_orig file
        f_file = reid_m.f_orig
        s_file = reid_m.anonymized

        return utility_scores, reid_scores, f_file, s_file

        return utility_scores, reid_scores, f_file


def main():
    """Main loop
    """
    # Lets assume the the ground_truth is a CSV file
    # and is present at data/ground_truth.csv
    # and a sample submission is present at data/sample_submission.csv
    answer_file_path = "data/ground_truth.csv"
    _client_payload = {}
    _client_payload["submission_file_path"] = "data/submission.csv"
    # Find a way to recover team name from submission
    # See with crawai
    _context = {'team_name':'a'}
    # Instantiate an evaluator
    crowdai_evaluator = DarcEvaluator(answer_file_path)
    # Evaluate
    result = crowdai_evaluator.evaluate(_client_payload, _context)
    print(result)

if __name__ == "__main__":
    main()
