"""
File: tsne_verification.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: Script to generate several t-sne to understand the dispertion in the data
"""

import sys
import getopt

from sklearn.manifold import TSE
import pandas as pd


def main():
    """main function

    """

    save_path = "."

    try:
        # Short option syntax: "hv:"
        # Long option syntax: "help" or "verbose="
        opts, args = getopt.getopt(sys.argv[1:], "hp:s:", ["help", "path", "save_path"])

    except getopt.GetoptError as err:
        # Print debug info
        print(str(err))
        sys.exit(1)

    for option, argument in opts:
        if option in ("-h", "--help"):
            sys.exit("tsne_verif --help --path: --save_path:")
        elif option in ("-p", "--path"):
            path = argument
        elif option in ("-s", "--save_path"):
            save_path = argument


if __name__ == "__main__":
    main()
