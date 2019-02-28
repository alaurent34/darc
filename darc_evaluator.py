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
import os
from io import BytesIO

import pandas as pd
import redis
import owncloud

try:
    from metrics import UtilityMetrics, ReidentificationMetrics
    from preprocessing import round1_preprocessing, round2_preprocessing, read_tar
    from utils import *
except ImportError:
    from .metrics import UtilityMetrics, ReidentificationMetrics
    from .preprocessing import round1_preprocessing, round2_preprocessing, read_tar
    from .utils import *


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

def save_first_round_attempt(team_id, at_data, s_data, f_data,\
                             crowdai_submission_id, redis_c, oc):
    """Save the attempt of team `team_id`. Attempt are stored as Y_CROWDAI_SUBMISSION_ID
    with Y in :
            - AT : the submission
            - S : AT with DEL row deleted
            - F : correspondance between id and pseudo

    :team_id: The id of the team submitting the anonymized file.
    :at_data: the submission
    :s_data: AT with DEL row deleted
    :f_data: correspondance between id and pseudo
    :crowdai_submission_id: the submission id in crowdai
    :redis_c: one working redis connection
    :oc: one working owncloud connection

    """
    nb_try = redis_c.llen("{}_id_sub".format(team_id))

    if nb_try == 3:
        id_sub = int(redis_c.lpop("{}_id_sub".format(team_id)))

        oc.delete("AT_{}.csv".format(id_sub))
        oc.delete("S_{}.csv".format(id_sub))
        oc.delete("F_{}.csv".format(id_sub))

        # ENLEVER id sub

    err = []
    err.append(oc.put_file_contents(
        data=at_data.to_csv(index=False),
        remote_path="AT_{}.csv".format(crowdai_submission_id)
        ))
    err.append(oc.put_file_contents(
        data=s_data.to_csv(index=False),
        remote_path="S_{}.csv".format(crowdai_submission_id)
        ))
    err.append(oc.put_file_contents(
        data=f_data.to_csv(index=False),
        remote_path="F_{}.csv".format(crowdai_submission_id)
        ))

    err.append(redis_c.rpush("{}_id_sub".format(team_id), crowdai_submission_id))

    if not min(err):
        raise Exception("Error while saving files for round 1")
        return False
    return True

class OwnCloudConnection():
    """
    Do the connection to owncloud data base
    """

    def __init__(self, host, usr, password):
        """
        init function
        """
        self._host = host
        self._usr = usr
        self._password = password
        self._oc = self._connect_to_bdd()

    def _connect_to_bdd(self):
        """Set the first connection
        :returns: connection

        """
        oc_client = owncloud.Client(self._host)
        oc_client.login(self._usr, self._password)

        return oc_client

    def get_oc_connection(self):
        """Return the connection to the owncloud data base
        """
        return self._oc

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
        self._redis_co = self._connect_to_bdd()


    def _connect_to_bdd(self):
        """Connect to the online BDD redis

        :returns: an instance of redis bdd

        """
        redis_co = redis.Redis(\
                    host=self._host,
                    port=self._port,
                    password=self._password)

        return redis_co

    def get_redis_connection(self):
        """Return the connection to the redis data base
        """
        return self._redis_co

    def get_nb_try_reid(self, team_name, attempt_attacked):
        """ Return the number of attempts the team as made against one opponent team and their
        submission dataset.

        :team_name: the name of the attacking team.
        :attempt_attacked: the file (1, 2, or 3) of the opponent team attacked.

        :return: Number of attempts made by team A against team B file.
        """

        # Return the number of attempts or 0 if there is no value at regis_get address.
        redis_get = "{}_vs_file_{}".format(team_name, attempt_attacked)
        return int(self._redis_co.get(redis_get) or 0)

    def set_nb_try_reid(self, nb_tries, team_name, attempt_attacked):
        """Set the number of attempts the team as made against one opponent team and their
        submission dataset.

        :nb_tries: the number of attempts to set
        :team_name: the name of the attacking team.
        :opponent_name: the name of the opponent team
        :attempt_attacked: the file (1, 2, or 3) of the opponent team attacked.

        """
        redis_set = "{}_vs_file_{}".format(team_name, attempt_attacked)
        self._redis_co.set(redis_set, nb_tries)


    def set_value(self, value, adress):
        """ Set the value into redis BDD.

        :value: the value to set into the redis BDD.
        :adress: the adress where to set the value.
        """
        return self._redis_co.set(adress, value)

    def get_value(self, adress):
        """ Get the value at adress `adress` into redis BDD.

        :adress: the adress where to get the value.
        """
        return self._redis_co.get(adress)


class DarcEvaluator():
    """
    Evaluate submission file of users in the context od DARC competition
    This is a fork from crowdai_evaluator https://github.com/crowdAI/crowdai-example-evaluator
    """
    def __init__(self, answer_file_path, round=1,
                 redis_host='127.0.0.1', redis_port=6379, redis_password=False,
                 oc_host="http://http://redisdarc.insa-cvl.fr:8080", oc_usr=False, oc_password=False
                ):
        """
        `round` : Holds the round for which the evaluation is being done.
        can be 1, 2...upto the number of rounds the challenge has.
        Different rounds will mostly have different ground truth files.
        """
        self.answer_file_path = answer_file_path
        self.round = round
        # Determine the score depending on the round
        self.redis_co = ""
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password

        self.oc_co = ""
        self.oc_host = oc_host
        self.oc_usr = oc_usr
        self.oc_password = oc_password


    def _evaluate(self, client_payload, _context={}):
        """
        `client_payload` will be a dict with (atleast) the following keys :
          - submission_file_path : local file path of the submitted file
          - crowdai_submission_id : A unique id representing the submission
          - crowdai_participant_id : A unique id for participant/team submitting (if enabled)
        """

        # Initialize redis_co
        self.redis_co = RedisConnection(self.redis_host, self.redis_port, self.redis_password)
        self.oc_co = OwnCloudConnection(self.oc_host, self.oc_usr, self.oc_password)

        # Initialize directory variable
        submission_file_path = client_payload["submission_file_path"]
        crowdai_submission_uid = client_payload["crowdai_participant_id"]
        crowdai_submission_id = client_payload["crowdai_submission_id"]


        ## ROUND 1
        if self.round == 1:

            # Read database from files
            ground_truth, aux_database, submission = round1_preprocessing(
                self.answer_file_path, submission_file_path
            )

            # Check the format of the Anonymized Transaction file
            check_format_trans_file(ground_truth, submission)

            # Determine all the scores for a anonymization transaction file
            utility_scores, reid_scores, f_file, s_file = compute_score_round1(
                ground_truth, aux_database, submission
            )

            err = save_first_round_attempt(
                crowdai_submission_uid,
                submission,
                s_file,
                f_file,
                crowdai_submission_id,
                self.redis_co.get_redis_connection(),
                self.oc_co.get_oc_connection()
                )

            if not err :
                raise Exception("Error while saving the files in first round")

            _result_object = {
                "score" : max(utility_scores),
                "score_secondary": max(reid_scores)
                }
            return _result_object

        # ROUND 2
        elif self.round == 2:

            #Read tar file
            submission_file_path, crowdai_submission_id_attacked = read_tar(
                submission_file_path
                )

            # Recover ground Truth from Redis database
            try:
                ground_truth = pd.read_csv(BytesIO(
                    self.oc_co.get_oc_connection().get_file_contents(
                        "F_{}.csv".format(crowdai_submission_id_attacked)
                        )
                    ))
            except ValueError:
                raise Exception("There is no team with submission number {}".format(
                    crowdai_submission_id_attacked
                    ))

            # Read submitted files and ground truth
            submission = round2_preprocessing(submission_file_path)

            # Check if they've attacked them 10 times already
            nb_atcks = self.redis_co.get_nb_try_reid(
                crowdai_submission_uid, crowdai_submission_id_attacked
                )
            if nb_atcks >= 10:
                raise Exception("You've reach your 10 attempts on this file.")

            # Compute score for round 2
            check_format_f_file(submission)
            reidentification_score = compute_score_round2(ground_truth, submission)

            # Increment by 1 the number of attempts
            self.redis_co.set_nb_try_reid(
                nb_atcks+1, crowdai_submission_uid, crowdai_submission_id_attacked
                )

            # Return object
            _result_object = {
                "score": reidentification_score,
                "score_secondary": 0
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
    _client_payload["submission_file_path"] = "data/example_files/submission_DEL.csv"
    # Name of the current team who is submitting the file
    # It **SHALL** not contains "_" char.
    _client_payload["crowdai_submission_id"] = 2

    RHOST = os.getenv("REDIS_HOST", False)
    RPORT = int(os.getenv("REDIS_PORT", 6379))
    RPASSWORD = os.getenv("REDIS_PASSWORD", False)

    OCHOST = os.getenv("OC_HOST", False)
    OCUSR = os.getenv("OC_USR", False)
    OCPASSWORD = os.getenv("OC_PASSWORD", False)

    if RHOST == False:
        raise Exception("Please provide the Redis Host and other credentials, by providing the following environment variables : REDIS_HOST, REDIS_PORT, REDIS_PASSWORD")
    if OCHOST == False:
        raise Exception("Please provide the OwnCloud Host and other credentials, by providing the following environment variables : OC_HOST, OC_USR, OC_PASSWORD")

    _context = {}
    # Instantiate an evaluator
    crowdai_evaluator = DarcEvaluator(
        answer_file_path, round=1,
        redis_host=RHOST, redis_port=RPORT, redis_password=RPASSWORD,
        oc_host=OCHOST, oc_usr=OCUSR, oc_password=OCPASSWORD
        )
    # Evaluate
    result = crowdai_evaluator._evaluate(
        _client_payload, _context
        )
    print(result)

    print("TESTING : Round 2")
    # Ground truth path for round 2
    # It is recovered during the round2 in method evaluate

    # Submission file for round 2
    _client_payload["submission_file_path"] = "./data/example_files/F_a_attempt_2.tar"

    # Instantiate an evaluator
    crowdai_evaluator = DarcEvaluator(
        answer_file_path, round=2,
        redis_host=RHOST, redis_port=RPORT, redis_password=RPASSWORD,
        oc_host=OCHOST, oc_usr=OCUSR, oc_password=OCPASSWORD
        )
    #Evaluate
    result = crowdai_evaluator._evaluate(
        _client_payload, _context
        )
    print(result)

if __name__ == "__main__":
    main()

