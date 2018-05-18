#!/usr/bin/env python

import pandas as pd
import numpy as np
import sys

def compute_mean_price_trans_qte(t_file, c_attr, price_attr="price", qte_attr="qte"):
    """
    Read the T_100, t_75 or t_25 file and output a new file with mean values.
    """
    data = pd.read_csv(t_file)
    bool = False
    for i in range(data.shape[0]):
        if (data[c_attr][i]=="DEL"):
            bool = True

    if (bool):
        data = data[data[c_attr] != "DEL"]

    c_ids = data[c_attr].value_counts().index.sort_values()

    transactions = []
    prices = []
    qtes = []
    for i in range(c_ids.shape[0]):
        tr = data[data[c_attr] == c_ids[i]]
        transactions.append(tr.shape[0] / 12.0)
        prices.append(tr[price_attr].sum() / float(tr.shape[0]))
        qtes.append(tr[qte_attr].sum() / float(tr.shape[0]))


    o = t_file.split(".")
    o[-2] += "_indiv_year_mean_transactions_prices_qtes_"
    pd.DataFrame(np.transpose([c_ids, transactions, prices, qtes]), columns=["id_user", "mean_transactions", "mean_prices", "mean_qtes"]).to_csv(".".join(o), index=False)


#compute_mean_price_trans_qte(t_file=sys.argv[2], c_attr=sys.argv[1])
