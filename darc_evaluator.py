import os
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

        # Determine the score depending on the round
        ## ROUND 1
        if self.round == 1:
            utility_scores, reid_scores, f_file = self._round1(ground_truth, aux_database,\
                                                               submission)

            # Save he AT file for each team
            team_directory = "./data/teams/{}".format(_context['team_name'])

            if not os.path.exists(team_directory):
                os.makedirs(team_directory)

            submission.to_csv("{}/AT.csv".format(team_directory), index=False)
            f_file.to_csv("{}/F.csv".format(team_directory), index=False)

            # Display to the player his scores on all metrics
            for i in range(len(utility_scores)):
                print("E{} : {}".format(i, utility_scores[i]))
            for i in range(len(reid_scores)):
                print("E{} : {}".format(i, reid_scores[i]))

            primary_score = max(utility_scores)
            secondary_score = max(reid_scores)

            # Save the best score for each team
            score_file = open("{}/scores.txt".format(team_directory), "w+")
            score_file.write("Utility score : {}".format(primary_score))
            score_file.write("Re-identification score : {}".format(secondary_score))
            score_file.close()

        # ROUND 2
        elif self.round == 2:
            pass

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
        :submission:
        :returns: TODO

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