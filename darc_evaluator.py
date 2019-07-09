"""
File: darc_evaluator.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: Evaluator used in the context of the DARC (Data Anonymization and Re-identification
Competition).
"""

import os
import logging

import pandas as pd
import redis

try:
    from darc_core.metrics import Metrics, utility_metric
    from darc_core.preprocessing import round1_preprocessing, round2_preprocessing, read_tar
    from darc_core.utils import check_format_f_file, check_format_trans_file
    from config import Config as config
except ImportError:
    from .darc_core.metrics import Metrics, utility_metric
    from .darc_core.preprocessing import round1_preprocessing, round2_preprocessing, read_tar
    from .darc_core.utils import check_format_f_file, check_format_trans_file
    from .config import Config as config

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
    This is a fork from aicrowd_evaluator https://github.com/AIcrowd/AIcrowd-example-evaluator
    """
    def __init__(self, answer_file_path, round=1,
                 redis_host='127.0.0.1', redis_port=6379, redis_password=False,
                 round2_storage=None
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
        self.round2_storage = round2_storage

    def _evaluate(self, client_payload, _context={}):
        """
        `client_payload` will be a dict with (atleast) the following keys :
          - submission_file_path : local file path of the submitted file
          - aicrowd_submission_id : A unique id representing the submission
          - aicrowd_participant_id : A unique id for participant/team submitting (if enabled)
        """

        # Initialize redis_co
        self.redis_co = RedisConnection(self.redis_host, self.redis_port, self.redis_password)

        # Initialize directory variable
        submission_file_path = client_payload["submission_file_path"]
        try:
            aicrowd_submission_uid = client_payload["crowdai_participant_id"]
            aicrowd_submission_id = client_payload["crowdai_submission_id"]
        except Exception:
            aicrowd_submission_uid = client_payload["aicrowd_participant_id"]
            aicrowd_submission_id = client_payload["aicrowd_submission_id"]


        ## ROUND 1
        if self.round == 1:

            # Read database from files
            ground_truth, submission = round1_preprocessing(
                self.answer_file_path, submission_file_path
            )

            # Check the format of the Anonymized Transaction file
            check_format_trans_file(ground_truth, submission)

            # Determine all the scores for a anonymization transaction file
            metric = Metrics(ground_truth, submission)
            scores = metric.scores()

            # TODO: This should be done only for the inter round submission (i.e. the final ones) <27-06-19, antoine> #
            # save score submission_reid for round2
            self.redis_co.set_value(f"{aicrowd_submission_id}", max(scores[6:12]))

            _result_object = {
                "score" : (max(scores[0:6]) + max(scores[6:13]))/2,
                "score_secondary": max(scores[0:6]),
                "meta" : {
                    "e1":scores[0],
                    "e2":scores[1],
                    "e3":scores[2],
                    "e4":scores[3],
                    "e5":scores[4],
                    "e6":scores[5],
                    "s1":scores[6],
                    "s2":scores[7],
                    "s3":scores[8],
                    "s4":scores[9],
                    "s5":scores[10],
                    "s6":scores[11],
                    "s7":scores[12]
                    }
                }
            return _result_object

        # ROUND 2
        elif self.round == 2:

            #Read tar file
            submission_file_path, aicrowd_submission_id_attacked = read_tar(
                submission_file_path
                )

            # Recover ground_truth
            ground_truth = round1_preprocessing(self.answer_file_path)

            # Read submitted files and ground truth
            submission = round2_preprocessing(submission_file_path)

            # Recover ground Truth from Redis database
            try:
                at_origin = pd.read_csv(f"{self.round2_storage}/{aicrowd_submission_id_attacked}.csv")
            except FileNotFoundError:
                raise Exception("There is no team with submission number {}".format(
                    aicrowd_submission_id_attacked
                    ))

            # Check if they've attacked them 10 times already
            nb_atcks = self.redis_co.get_nb_try_reid(
                aicrowd_submission_uid, aicrowd_submission_id_attacked
                )
            if nb_atcks >= 10:
                raise Exception("You've reach your 10 attempts on this file.")

            # Compute score for round 2
            check_format_f_file(submission)

            metrics = Metrics(ground_truth, at_origin)
            reidentification_score = metrics.compare_f_files(submission)

            # Increment by 1 the number of attempts
            self.redis_co.set_nb_try_reid(
                nb_atcks+1, aicrowd_submission_uid, aicrowd_submission_id_attacked
                )

            # Update score of submission
            previous_score = float(self.redis_co.get_value(aicrowd_submission_id_attacked) or 0)
            attack_success = False
            attck_sc = float(self.redis_co.get_value(f"{aicrowd_submission_id}_attck_sc") or 0)

            if previous_score < reidentification_score:
                self.redis_co.set_value(reidentification_score, aicrowd_submission_id_attacked)
                attack_success = True
                diff_sc = reidentification_score - previous_score
                attck_sc = attck_sc + diff_sc

            nb_atcks_success = int(
                self.redis_co.get_value(f"{aicrowd_submission_id}_attck_succ") or 0
            )
            if attack_success:
                nb_atcks_success += 1
                self.redis_co.set_value(nb_atcks_success, f"{aicrowd_submission_id}_attck_succ")

            # Compute the attack score as the mean of all attacks
            if nb_atcks_success > 0:
                attck_sc /= nb_atcks_success
            else:
                attck_sc = 0

            # Return object
            _result_object = {
                "score": reidentification_score,
                "score_secondary": attck_sc
                }

            # Remove submission_file extracted
            os.remove(submission_file_path)

            return _result_object

        return None

def main():
    """Main loop
    """
    #log file when Docker is launch
    try:
        logging.basicConfig(filename='/test/darc.log', level=logging.DEBUG)
    except Exception:
        pass

    answer_file_path = config.GROUND_TRUTH

    _client_payload = {}

    # Setting name of submitting team
    _client_payload["aicrowd_participant_id"] = "a"

    logging.info("TESTING: Round 1")

    # Ground truth path for round 1
    _client_payload["submission_file_path"] = config.R1_SUBMISSION_FILE

    # Setting the submission id
    _client_payload["aicrowd_submission_id"] = 2

    # Reading info for stockage server
    RHOST = config.REDIS_HOST
    RPORT = config.REDIS_PORT
    RPASSWORD = config.REDIS_PASSWORD

    if not RHOST:
        raise Exception("Please provide the Redis Host and other credentials, by providing the following environment variables : REDIS_HOST, REDIS_PORT, REDIS_PASSWORD")

    _context = {}

    # Instantiate an evaluator
    aicrowd_evaluator = DarcEvaluator(
        answer_file_path, round=1,
        redis_host=RHOST, redis_port=RPORT, redis_password=RPASSWORD
        )

    # Evaluate
    result = aicrowd_evaluator._evaluate(
        _client_payload, _context
        )

    logging.info(f"Scores : {result}")

    logging.info("TESTING : Round 2")

    # Submission file for round 2
    _client_payload["submission_file_path"] = config.R2_SUBMISSION_FILE

    # Instantiate an evaluator
    aicrowd_evaluator = DarcEvaluator(
        answer_file_path, round=2,
        redis_host=RHOST, redis_port=RPORT, redis_password=RPASSWORD,
        round2_storage = config.ROUND2_STORAGE
        )

    #Evaluate
    result = aicrowd_evaluator._evaluate(
        _client_payload, _context
        )

    logging.info(f"Scores : {result}")

if __name__ == "__main__":
    main()
