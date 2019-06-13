import os
from darc_core.metrics import Metrics

class Config:
    REDIS_HOST=os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT=os.environ.get("REDIS_PORT", 6379)
    REDIS_PASSWORD=os.environ.get("REDIS_PASSWORD", False)

    OC_HOST=os.environ.get("OC_HOST", "localhost")
    OC_USR=os.environ.get("OC_USR", "test")
    OC_PASSWORD=os.environ.get("OC_PASSWORD", "password")

    GROUND_TRUTH = "data/ground_truth.csv"
    R1_SUBMISSION_FILE = "data/example_files/submission_DEL.csv"
    R2_SUBMISSION_FILE = "./data/example_files/F_a_attempt_2.tar"
    TESTING_DIR = "data/testing_files/"

    metric_class = Metrics
