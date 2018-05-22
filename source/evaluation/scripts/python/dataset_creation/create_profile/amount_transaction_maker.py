#!/usr/bin/env python

import pandas as pd
import sys

def customer_amount_per_months(t_500, c_attr, date_attr, qte_attr="qte", price_attr="price"):
    """
    Create a csv with the amount expended by each customer per month.
    This file read the t_100, t_25 or t_75 file.
    """

    t_5 = pd.read_csv(t_500)
    t_5 = t_5[t_5[c_attr].astype("str")!= "DEL"]
    c_ids = t_5[c_attr].value_counts().index.sort_values()
    month = 12
    year = 2010
    o_frame = pd.DataFrame(c_ids, columns=[c_attr])
    t_frame = pd.DataFrame(c_ids, columns=[c_attr])
    m_qte_frame = pd.DataFrame(c_ids, columns=[c_attr])
    m_exp_frame = pd.DataFrame(c_ids, columns=[c_attr])
    m_price_frame = pd.DataFrame(c_ids, columns=[c_attr])

    def month_expenses(m_5_c, t_5_m):
        m_expenses = []
        t_transact = []
        mean_price = []
        mean_qte = []
        mean_exp = []
        for i in range(m_5_c.shape[0]):
            t_custm = t_5_m[ t_5_m[c_attr] == m_5_c[i] ]
            t_transact.append(t_custm.shape[0])
            if t_custm.shape[0] != 0:
                m_expenses.append((t_custm[qte_attr] * t_custm[price_attr]).sum())
            else:
                m_expenses.append(0)
            if t_transact[-1] != 0:
                mean_exp.append(m_expenses[-1] / float(t_transact[-1]))
                mean_price.append(t_custm[price_attr].sum() / float(t_transact[-1]))
                mean_qte.append(t_custm[qte_attr].sum() / float(t_transact[-1]))
            else:
                mean_exp.append(0)
                mean_price.append(0)
                mean_qte.append(0)
        return m_expenses, t_transact, mean_exp, mean_price, mean_qte

    m_exp, t_transat, mean_exp, m_price, m_qte = month_expenses(c_ids, t_5[t_5[date_attr].str.contains("{y}/{m}/".format(y=year, m=month))])
    o_frame = pd.concat([o_frame, pd.DataFrame(m_exp, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)
    t_frame = pd.concat([t_frame, pd.DataFrame(t_transat, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)
    m_exp_frame = pd.concat([m_exp_frame, pd.DataFrame(mean_exp, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)
    m_qte_frame = pd.concat([m_qte_frame, pd.DataFrame(m_qte, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)
    m_price_frame = pd.concat([m_price_frame, pd.DataFrame(m_price, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)

    year += 1
    for month in range(1,12):
        m_exp, t_transat, mean_exp, m_price, m_qte = month_expenses(c_ids, t_5[t_5[date_attr].str.contains("{y}/{m}/".format(y=year, m=month))])
        o_frame = pd.concat([o_frame, pd.DataFrame(m_exp, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)
        t_frame = pd.concat([t_frame, pd.DataFrame(t_transat, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)
        m_exp_frame = pd.concat([m_exp_frame, pd.DataFrame(mean_exp, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)
        m_qte_frame = pd.concat([m_qte_frame, pd.DataFrame(m_qte, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)
        m_price_frame = pd.concat([m_price_frame, pd.DataFrame(m_price, columns=["{y}/{m}".format(y=year, m=month)])], axis=1)

    o = t_500.split(".")
    o[-2] += "_c_expenses_per_month_"
    o_frame.to_csv(".".join(o), index=False)
    o = t_500.split(".")
    o[-2] += "_transactions_per_month_"
    t_frame.to_csv(".".join(o), index=False)
    o = t_500.split(".")
    o[-2] += "_c_mean_expenses_per_month_"
    m_exp_frame.to_csv(".".join(o), index=False)
    o = t_500.split(".")
    o[-2] += "_c_mean_qte_per_month_"
    m_qte_frame.to_csv(".".join(o), index=False)
    o = t_500.split(".")
    o[-2] += "_c_mean_price_per_month_"
    m_price_frame.to_csv(".".join(o), index=False)



#customer_amount_per_months(t_500=sys.argv[1], c_attr="CustomerID", date_attr="TransactionDate", qte_attr="qte", price_attr="price")
