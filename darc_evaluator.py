"""
File: darc_evaluator.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: Evaluator used in the context of the DARC (Data Anonymization and Re-identification
Competition).
"""

from multiprocessing import Pool
from functools import partial

import pandas as pd
import redis

from utils import *
import metrics
import preprocessing

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
    utility_m = metrics.UtilityMetrics(aux_database, ground_truth, submission)

    #Compute utility metrics as subprocesses
    print("Compute Utility metrics")
    metric_pool = Pool()
    utility_wrapper = partial(metric_wrapper, "e", utility_m)
    utility_scores = metric_pool.map(utility_wrapper, range(1, 7))

    # Initialize re-identification metrics
    reid_m = metrics.ReidentificationMetrics(aux_database, ground_truth, submission)

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

class RedisConnection():

    """Class to control redis data base and stock team submission scores.
    The data base is store by the organizator of the competition

    """

    def __init__(self, host, port, password):
        """Initialization method

        :host: adresse of the host for the redis data base.
        :port: port for the host.
        :password: password of the data base.
        """
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

    def get_nb_try_reid(self, team_name, opponent_name, attempt_attacked):
        """ Return the number of attempts the team as made against one opponent team and their
        submission dataset.

        :team_name: the name of the attacking team.
        :opponent_name: the name of the opponent team
        :attempt_attacked: the file (1, 2, or 3) of the opponent team attacked.

        :return: Number of attempts made by team A against team B file.
        """

        # Return the number of attempts or 0 if there is no value at regis_get address.
        redis_get = "{}_vs_{}_file_{}".format(team_name, opponent_name, attempt_attacked)
        return int(self._redis_co.get(redis_get) or 0)

    def set_nb_try_reid(self, nb_trys, team_name, opponent_name, attempt_attacked):
        """Set the number of attempts the team as made against one opponent team and their
        submission dataset.

        :nb_trys: the number of attempts to set
        :team_name: the name of the attacking team.
        :opponent_name: the name of the opponent team
        :attempt_attacked: the file (1, 2, or 3) of the opponent team attacked.

        """
        redis_set = "{}_vs_{}_file_{}".format(team_name, opponent_name, attempt_attacked)
        self._redis_co.set(redis_set, nb_trys)

    def save_first_round_attempt(self, team_name, at_data, s_data, f_data, score_util, score_reid,\
                                 crowdai_submission_id):
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
        pipe = self._redis_co.pipeline()
        # Save AT on redis BDD
        pipe.set("AT_{}_submission_id_{}".format(team_name, crowdai_submission_id),\
                                               at_data.to_msgpack(compress='zlib'))
        # Save S on redis BDD
        pipe.set("S_{}_submission_id_{}".format(team_name, crowdai_submission_id),\
                                              s_data.to_msgpack(compress='zlib'))
        # Save F on redis BDD
        pipe.set("F_{}_submission_id_{}".format(team_name, crowdai_submission_id),\
                                              f_data.to_msgpack(compress='zlib'))
        # Save utility score in redis BDD
        pipe.set("score_util_{}_submission_id_{}".format(team_name, crowdai_submission_id),\
                                                       score_util)
        # Save re-identification score in redis BDD
        pipe.set("score_reid_{}_submission_id_{}".format(team_name, crowdai_submission_id),\
                                                       score_reid)
        pipe.execute()

    def set_value(self, value, adress):
        """ Set the value into redis BDD.

        :value: the value to set into the redis BDD.
        :adress: the adress where to set the value.
        """
        self._redis_co.set(adress, value)

    def get_value(self, adress):
        """ Get the value at adress `adress` into redis BDD.

        :adress: the adress where to get the value.
        """
        return self._redis_co.get(adress)


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
        # Determine the score depending on the round
        self.redis_co = ""

    def evaluate(self, client_payload, _context={}, redis_host="", redis_port="", redis_password=""):
        """
        `client_payload` will be a dict with (atleast) the following keys :
          - submission_file_path : local file path of the submitted file
          - crowdai_submission_id : A unique id representing the submission
          - crowdai_participant_id : A unique id for participant/team submitting (if enabled)
        """

        # Initialize redis_co
        self.redis_co = RedisConnection(redis_host, redis_port, redis_password)

        # Initialize directory variable
        submission_file_path = client_payload["submission_file_path"]
        crowdai_submission_uid = client_payload["crowdai_participant_id"]
        crowdai_submission_id = client_payload["crowdai_submission_id"]


        ## ROUND 1
        if self.round == 1:

            # Read database from files
            ground_truth, aux_database, submission = preprocessing.round1_preprocessing(\
                                                            self.answer_file_path,\
                                                            submission_file_path)

            # Check the format of the Anonymized Transaction file
            check_format_trans_file(submission)

            # Determine all the scores for a anonymization transaction file
            utility_scores, reid_scores, f_file, s_file = compute_score_round1(\
                                                               ground_truth,\
                                                               aux_database,\
                                                               submission)

            # Save all informations about this attempt and get 3 last scores, it's a **list of dic**
            print("Saving scores and files")
            self.redis_co.save_first_round_attempt(crowdai_submission_uid,\
                                                   submission,\
                                                   s_file,\
                                                   f_file,\
                                                   utility_scores,\
                                                   reid_scores,\
                                                   crowdai_submission_id)

            _result_object = {
                "utility_score" : max(utility_scores),
                "reidentification_score": max(reid_scores)
                }
            return _result_object

        # ROUND 2
        elif self.round == 2:

            #Read tar file
            submission_file_path, team_attacked, crowdai_submission_id = preprocessing.read_tar(
                submission_file_path
                )

            # Recover ground Truth from Redis database
            try:
                ground_truth = pd.read_msgpack(self.redis_co.get_value(
                    "F_{}_submission_id_{}".format(team_attacked, crowdai_submission_id)
                    ))
            except ValueError:
                raise Exception("There is no team {} with submission number {}".format(
                    team_attacked, crowdai_submission_id
                    ))

            # Read submitted files and ground truth
            submission = preprocessing.round2_preprocessing(submission_file_path,\
                                                                crowdai_submission_id,\
                                                                team_attacked)

            # Check if they've attacked them 10 times already
            nb_atcks = self.redis_co.get_nb_try_reid(
                crowdai_submission_uid, team_attacked, crowdai_submission_id
                )
            if nb_atcks >= 10:
                raise Exception("You've reach your 10 attempts on this file.")

            # Compute score for round 2
            check_format_f_file(submission)
            reidentification_score = compute_score_round2(ground_truth, submission)

            # Increment by 1 the number of attempts
            self.redis_co.set_nb_try_reid(
                nb_atcks+1, crowdai_submission_uid, team_attacked, crowdai_submission_id
                )

            # Return object
            _result_object = {
                "reidentification_score": reidentification_score,
                }

            # Remove submission_file extracted
            os.remove(submission_file_path)

            return _result_object

        return None

def main():
    """Main loop
    """
    answer_file_path = "data/ground_truth.csv"

    _client_payload = {}
    # The submission file of the team
    # For the round 1 : the anonymized transactional database
    # For the round 2 : a tar file containing :
    #                       - The F_file of the team attacked.
    #                       - A json file containing the two following attributes :
    #                       'submission_id_attacked' and 'submission_id_attacked'
    #

    _client_payload["crowdai_participant_id"] = "a"

    print("TESTING: Round 1")

    # Ground truth path for round 1
    _client_payload["submission_file_path"] = "data/example_files/submission.csv"
    # Name of the current team who is submitting the file
    # It **SHALL** not contains "_" char.
    _client_payload["crowdai_submission_id"] = 2

    _context = {}
    # Instantiate an evaluator
    crowdai_evaluator = DarcEvaluator(answer_file_path, round=1)
    # Evaluate
    result = crowdai_evaluator.evaluate(
        _client_payload, _context, redis_host=HOST, redis_port=PORT, redis_password=PASSWORD
        )
    print(result)

    print("TESTING : Round 2")
    # Ground truth path for round 2
    # It is recovered during the round2 in method evaluate

    # Submission file for round 2
    _client_payload["submission_file_path"] = "./data/example_files/F_a_attempt_2.tar"

    # Instantiate an evaluator
    crowdai_evaluator = DarcEvaluator(answer_file_path, round=2)
    #Evaluate
    result = crowdai_evaluator.evaluate(
        _client_payload, _context, redis_host=HOST, redis_port=PORT, redis_password=PASSWORD
        )
    print(result)

if __name__ == "__main__":
    main()
