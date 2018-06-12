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
import datetime

import pandas as pd

C_MIN = 5
C_MAX = 500
COL = {"id_user":"CustomerID", "date":"InvoiceDate", "hours":"heure"}
NEW_COLS = ['InvoiceNo', 'id_item', 'Description', 'qte',\
            'date', 'price', 'id_user', 'Country', 'heure']

def get_id_with_count_between(data, c_min, c_max):
    """ recover all id of user that have a transaction count between c_min and c_max in data

    :data: the dataframe with columns == col
    :c_min: the minimum number of trajectory that all user must possess.
    :c_max: the maximum number of trajectory that all user must possess.

    :returns: the list of all user id that satisfy the condition

    """
    sup_c_min = data[COL['id_user']]\
                .value_counts()[data[COL['id_user']]\
                .value_counts() >= c_min].index
    inf_c_max = data[COL['id_user']]\
                .value_counts()[data[COL['id_user']]\
                .value_counts() <= c_max].index

    inter = set(inf_c_max).intersection(set(sup_c_min))

    return list(inter)

def transform_date_pwscup_way(data):
    """Transform date to mach the date format from PWSCup to be able to use the script efficiently.

    :data: the DataFrame to transform

    :returns: the DataFrame transformed

    """
    data[COL["date"]] = pd.to_datetime(data[COL["date"]], format='%Y-%m-%d %H:%M:%S')

    def get_date(date):
        """Get date from timestamp
        """
        return date.date()
    def get_time(date):
        """Get hours:minute:sec from timestamp
        """
        return date.time()
    def format_date(date):
        """Format date to match string
        """
        return date.strftime('%Y/%m/%d')
    def format_time(hour):
        """Format time to match string
        """
        return hour.strftime('%H:%M')

    data.loc[:, COL['hours']] = data[COL['date']].apply(lambda x: get_time(x))
    data.loc[:, COL['date']] = data[COL['date']].apply(lambda x: get_date(x))

    data.loc[:, COL['date']] = data[COL['date']].apply(lambda x: format_date(x))
    data.loc[:, COL['hours']] = data[COL['hours']].apply(lambda x: format_time(x))

    return data

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

    #recover the list of user of interest (uoi)
    list_uoi = get_id_with_count_between(data, C_MIN, C_MAX)

    data = data.loc[data['CustomerID'].isin(list_uoi)]
    data = data.reset_index(drop=True)

    data = transform_date_pwscup_way(data)

    #change columns for extract_profile scripts
    data.columns = NEW_COLS

    data.to_csv("{}/data_extracted_{}-{}_traj.csv".format(save_path, C_MIN, C_MAX), index=False)


if __name__ == "__main__":
    main()
