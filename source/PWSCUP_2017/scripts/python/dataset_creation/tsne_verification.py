"""
File: tsne_verification.py
Author: Antoine Laurent
Email: laurent.antoine@courrier.uqam.ca
Github: https://github.com/Drayer34
Description: Script to generate several t-sne to understand the dispertion in the data
"""

import sys
import getopt

import progressbar
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

PERPLEXITY = [10, 20, 30, 50]

def save_fig_tsne(data, save_path, perplexity=20):
    """ calculate and save figure of t-sne for a certain perplexity

    :perplexity: the perplexity parameter in t-sne
    """
    tsne = TSNE(perplexity=perplexity).fit_transform(data)
    plt.clf()
    plt.scatter(tsne[:, 0], tsne[:, 1])
    plt.savefig('{}/tsne_p{}.png'.format(save_path, perplexity))

def main():
    """main function

    """

    save_path = "."

    try:
        # Short option syntax: "hv:"
        # Long option syntax: "help" or "verbose="
        opts, _ = getopt.getopt(sys.argv[1:], "hp:s:", ["help", "path", "save_path"])

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

    data = pd.read_csv(path)
    data = data.drop("id_user", axis=1)
    data = data.drop("id_items_usr", axis=1)

    pbar = progressbar.ProgressBar()

    for perplexity in pbar(PERPLEXITY):
        save_fig_tsne(data, save_path, perplexity)

if __name__ == "__main__":
    main()
