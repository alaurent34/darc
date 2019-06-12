from .metrics import Metrics

class Config:
    GROUND_TRUTH = "data/ground_truth.csv"
    TESTING_DIR = "data/testing_files/"

    metric_class = Metrics
