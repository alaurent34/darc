# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import pandas as pd
import sys
import numpy
from  amount_transaction_maker import customer_amount_per_months
from mean_year_price_trans_qte import compute_mean_price_trans_qte
import progressbar


def extract_profile(f=sys.argv[1]):

    f = pd.read_csv(f)

    bool = False
    for i in range(f.shape[0]):
        if (f['id_user'][i]=="DEL"):
            bool = True

    if (bool):
        f = f[f['id_user'] != "DEL"]

    o1 = sys.argv[1].split('.')
    o1[-2] += "_transactions_per_month_"
    o1 = pd.read_csv(".".join(o1))

    o2 = sys.argv[1].split('.')
    o2[-2] += "_c_expenses_per_month_"
    o2 = pd.read_csv(".".join(o2))
    o2 = o2.drop('id_user', axis=1)

    o3 = sys.argv[1].split('.')
    o3[-2] += "_c_mean_expenses_per_month_"
    o3 = pd.read_csv(".".join(o3))
    o3 = o3.drop('id_user', axis=1)

    o4 = sys.argv[1].split('.')
    o4[-2] += "_c_mean_qte_per_month_"
    o4 = pd.read_csv(".".join(o4))
    o4 = o4.drop('id_user', axis=1)

    o5 = sys.argv[1].split('.')
    o5[-2] += "_c_mean_price_per_month_"
    o5 = pd.read_csv(".".join(o5))
    o5 = o5.drop('id_user', axis=1)

    bar = progressbar.ProgressBar()
    result = pd.concat([o1,o2,o3,o4,o5], axis=1)
    result.columns = ['id_user', 'dec', 'jan', 'fev', 'mar', 'avr', 'mai', 'jun', 'jui', 'aou', 'sep', 'oct', 'nov', '1dec', '1jan', '1fev', '1mar', '1avr', '1mai', '1jun', '1jui', '1aou', '1sep', '1oct', '1nov', '2dec', '2jan', '2fev', '2mar', '2avr', '2mai', '2jun', '2jui', '2aou', '2sep', '2oct', '2nov', '3dec', '3jan', '3fev', '3mar', '3avr', '3mai', '3jun', '3jui', '3aou', '3sep', '3oct', '3nov', '4dec', '4jan', '4fev', '4mar', '4avr', '4mai', '4jun', '4jui', '4aou', '4sep', '4oct', '4nov']


    o6 = sys.argv[1].split('.')
    o6[-2] += "_indiv_year_mean_transactions_prices_qtes_"
    o6 = pd.read_csv(".".join(o6))
    o6 = o6.drop('id_user', axis=1)

    result = pd.concat([result, o6], axis=1)


    o=[]
    bar = progressbar.ProgressBar()
    for idx in bar(range(result.shape[0])):
        o.append(o1.iloc[idx].drop('id_user').sum())

    result = pd.concat([result,pd.DataFrame(o, columns=['trans_mean'])], axis=1)

    t = f['id_user'].value_counts().index.sort_values()
    o = []
    bar = progressbar.ProgressBar()
    for i in bar(range(t.shape[0])):
        o.append(str(f[f['id_user'] == t[i]]['id_item'].value_counts().index.sort_values().format()))

    result = pd.concat([result,pd.DataFrame(o, columns=['id_items_usr'])], axis=1)

    str_result = sys.argv[1].split('.')
    str_result[-2] += "_profile_id_"
    result.to_csv(".".join(str_result), index=False)


if __name__=="__main__":
    customer_amount_per_months(t_500=sys.argv[1], c_attr="id_user", date_attr="date", qte_attr="qte", price_attr="price")
    compute_mean_price_trans_qte(t_file=sys.argv[1], c_attr="id_user")
    main()
