import pandas as pd
import numpy as np

class ExampleEvaluator:
  def __init__(self, answer_file_path, round=1):
    """
    `round` : Holds the round for which the evaluation is being done.
    can be 1, 2...upto the number of rounds the challenge has.
    Different rounds will mostly have different ground truth files.
    """
    self.answer_file_path = answer_file_path
    self.round = round

  def _evaluate(self, client_payload, _context={}):
    """
    `client_payload` will be a dict with (atleast) the following keys :
      - submission_file_path : local file path of the submitted file
    """
    submission_file_path = client_payload["submission_file_path"]
    submission = pd.read_csv(submission_file_path)
    # Or your preferred way to read your submission

    """
    Do something with your submitted file to come up
    with a score and a secondary score.

    if you want to report back an error to the user,
    then you can simply do :
      `raise Exception("YOUR-CUSTOM-ERROR")`

     You are encouraged to add as many validations as possible
     to provide meaningful feedback to your users
    """
    _result_object = {
        "score": np.random.random(),
        "score_secondary" : np.random.random()
    }
    return _result_object

if __name__ == "__main__":
    # Lets assume the the ground_truth is a CSV file
    # and is present at data/ground_truth.csv
    # and a sample submission is present at data/sample_submission.csv
    answer_file_path = "data/ground_truth.csv"
    _client_payload = {}
    _client_payload["submission_file_path"] = "data/sample_submission.csv"
    # Instaiate a dummy context
    _context = {}
    # Instantiate an evaluator
    crowdai_evaluator = ExampleEvaluator(answer_file_path)
    # Evaluate
    result = crowdai_evaluator._evaluate(_client_payload, _context)
    print(result)
