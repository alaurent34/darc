"""
File: extract_transaction.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: This script is used to extract transaction in the data set Online record
(http://archive.ics.uci.edu/ml/datasets/online+retail) for the anonymisation competition DARC.  We
want here to extract transaction that are not unique for a specific user (user with hight number of
transaction and user with low number of transaction).
"""

import sys
import getopt

import pandas as pd

C_MIN = 5
C_MAX = 500

def main():
    """Main function

    :returns: TODO

    """

    #default path for saving dataframe
    save_path = '.'

    try:
        # Short option syntax: "hv:"
        # Long option syntax: "help" or "verbose="
        opts, _ = getopt.getopt(sys.argv[1:], "hp:s:", ["help", "path", "save"])

    except getopt.GetoptError as err:
        # Print debug info
        print(str(err))
        sys.exit("extract_transaction --help --path: --save:")

    for option, argument in opts:
        if option in ("-h", "--help"):
            sys.exit("extract_transaction --help --path: --save:")
        elif option in ("-p", "--path"):
            path = argument
        elif option in ("-s", "--save"):
            save_path = argument

    data = pd.read_csv(path)

    data.to_csv("{}/data_extracted_{}-{}_traj.csv".format(save_path, C_MIN, C_MAX), index=False)
if __name__ == "__main__":
    main()
