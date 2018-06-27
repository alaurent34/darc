"""
File: darc_evaluator.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: TODO
"""

import os
import os.path
import pickle

import pandas as pd
import numpy as np
import redis

from utils import *
import metrics

class RedisConnection(object):

    """Docstring for RedisConnection. """

    def __init__(self, host, port, password):
        """TODO: to be defined1. """
        self._host = host
        self._port = port
        self._password = password
        self._redis_co = self.connect_to_bdd()


    def connect_to_bdd(self):
        """Connect to the online BDD redis

        :returns: an instance of redis bdd

        """
        redis_co = redis.Redis(\
                    host=self._host,
                    port=self._port,
                    password=self._password)

        return redis_co

    def get_nb_try_reid(self, team_name, opponent_name, submission_number):
        """ Return the number of attempts the team as made against one opponent team and their
        submission dataset.

        :team_name: the name of the attacking team.
        :opponent_name: the name of the opponent team
        :submission_number: the file (1, 2, or 3) of the opponent team attacked.

        :return: Number of attempts made by team A against team B file.
        """

        # Return the number of attempts or 0 if there is no value at regis_get address.
        redis_get = "{}_vs_{}_file_{}".format(team_name, opponent_name, submission_number)
        return int(self._redis_co.get(redis_get)) or 0

    def set_nb_try_reid(self, nb_trys, team_name, opponent_name, submission_number):
        """Set the number of attempts the team as made against one opponent team and their
        submission dataset.

        :nb_trys: the number of attempts to set
        :team_name: the name of the attacking team.
        :opponent_name: the name of the opponent team
        :submission_number: the file (1, 2, or 3) of the opponent team attacked.

        """
        redis_set = "{}_vs_{}_file_{}".format(team_name, opponent_name, submission_number)
        self._redis_co.set(redis_set, nb_trys)

    def get_three_last_scores(self, team_name):
        """Recover the three last scores for a team. This is done for displaying three latest
        submission in crowdAI platform.

        :team_name: The name of the team submitting the anonymized file.
        :returns: list of all the scores.

        """
        scores = []

        for i in range(3):
            scores[i] = {}
            scores[i]["utility_score"] = max(self._redis_co.get("score_util_{}_attempt_{}"\
                                                     .format(team_name, i))) or 'Not computed yet'
            scores[i]["reid_score"] = max(self._redis_co.get("score_util_{}_attempt_{}"\
                                                     .format(team_name, i))) or 'Not computed yet'

        return scores

    def save_first_round_attempt(self, team_name, at_data, s_data, f_data, score_util, score_reid):
        """Save the attempt of team `team_name`. Attempt are stored as Y_TEAM_NAME_attempt_X
        with Y in :
                - AT : the submission
                - S : AT with DEL row deleted
                - F : correspondance between id and pseudo
                - score_util : utility score for AT
                - score_reid : re-identification score for S
        and X in {0, 1, 2}, the attempt number

        :team_name: The name of the team submitting the anonymized file.
        :at_data: the submission
        :s_data: AT with DEL row deleted
        :f_data: correspondance between id and pseudo
        :score_util: utility score for AT
        :score_reid: re-identification score for S

        """
        nb_attempts = self._redis_co.get("{}_nb_attempts_ano".format(team_name))

        if not nb_attempts:
            nb_attempts = 0

        # Save AT on redis BDD
        self._redis_co.set("AT_{}_attempt_{}".format(team_name, nb_attempts),\
                                               at_data.to_msgpack(compress='zlib'))
        # Save S on redis BDD
        self._redis_co.set("S_{}_attempt_{}".format(team_name, nb_attempts),\
                                              s_data.to_msgpack(compress='zlib'))
        # Save F on redis BDD
        self._redis_co.set("F_{}_attempt_{}".format(team_name, nb_attempts),\
                                              f_data.to_msgpack(compress='zlib'))
        # Save utility score in redis BDD
        self._redis_co.set("score_util_{}_attempt_{}".format(team_name, nb_attempts),\
                                                       score_util)
        # Save re-identification score in redis BDD
        self._redis_co.set("score_reid_{}_attempt_{}".format(team_name, nb_attempts),\
                                                       score_reid)

        scores = self.get_three_last_scores(team_name)

        self._redis_co.set("{}_nb_attempts_ano".format(team_name), (nb_attempts + 1)%3)

        return scores


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

        # Initialize directory variable
        team = _context['team_name']
        # Determine the score depending on the round
        redis_co = RedisConnection(HOST, PORT, PASSWORD)

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

            # Save all informations about this attempt and get 3 last scores
            _result_object = redis_co.save_first_round_attempt(team, submission, s_file, f_file,\
                                                      utility_scores, reid_scores)

            return _result_object

        # ROUND 2
        elif self.round == 2:

            # Initialisation of parameters
            submission_file_path = client_payload["submission_file_path"]

            sub_file_name = submission_file_path.split('/')[-1]
            infos = "_".join(sub_file_name.split("_")[1:]).split('.')[0]

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

            reidentification_score = score_reid

            nb_atcks +=1
            with open("./data/teams/aux/{}_vs_{}".format(team, sub_file_name), "wb") as file_nb_atcks:
                pickle.dump(nb_atcks, file_nb_atcks)

            # Return object
            _result_object = {
                "reidentification_score": reidentification_score,
                }

            return _result_object

        return None

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

    def _round2(self, ground_truth, submission):
        """ Return the re-identification score done by the team submitting on the file anonymized by
        another team.

        It's the score of this team we have to move in the classement.
        :returns: the re-identification score obtained by the anonymized file.

        """
        return compare_f_files(ground_truth, submission)

def main():
    """Main loop
    """
    print("TESTING: Round 1")
    # Ground truth path for round 1
    answer_file_path = "data/ground_truth.csv"

    _client_payload = {}
    # The submission file of the team
    # For the round 1 : the anonymized transactional database
    # For the round 2 : the F_hat guessed by the team
    #                   It consist on the attack done by team submitting to the anonymized
    #                   transaction of an other team (S).
    #
    #                   The name of the S file is formatted as follow :
    #                   S_[team_name]_[anon_name]_[timestamp] and the F_hat file shall have the same
    #                   format as the S file attacked. For example if S file is :
    #                   S_mySuperTeam_attack1_1529601853639.csv, then the F_hat file should be
    #                   F_a_toto_1529601853639.csv
    _client_payload["submission_file_path"] = "data/submission.csv"
    # Name of the anonymized transaction file (round 1) else ""
    _client_payload["anon_name"] = "toto"

    _context = {}
    # Name of the current team who is submitting the file
    _context["team_name"] = "a"
    # Instantiate an evaluator
    crowdai_evaluator = DarcEvaluator(answer_file_path, round=1)
    # Evaluate
    result = crowdai_evaluator.evaluate(_client_payload, _context)
    print(result)

    print("TESTING : Round 2")
    # Ground truth path for round 2
    # It is recovered during the round2 in method evaluate

    # Submission file for round 2
    _client_payload["submission_file_path"] = os.listdir("./data/teams/F_files/")[0]

    # Instantiate an evaluator
    crowdai_evaluator = DarcEvaluator(answer_file_path, round=2)
    #Evaluate
    result = crowdai_evaluator.evaluate(_client_payload, _context)
    print(result)

if __name__ == "__main__":
    main()
