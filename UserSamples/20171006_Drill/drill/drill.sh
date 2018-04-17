#!/usr/bin/env sh



####### given data
M="./given_data/M.txt"
T="./given_data/T.txt"
T25="./given_data/T25.txt"
T50="./given_data/T50.txt"
T75="./given_data/T75.txt"
T100="./given_data/T100.txt"



####### anonymized data
AT="./at_data/AT_sample.txt"
Fh25_user="./f_hat/Fh25_sample.txt"
Fh50_user="./f_hat/Fh50_sample.txt"
Fh75_user="./f_hat/Fh75_sample.txt"
Fh100_user="./f_hat/Fh100_sample.txt"



####### make template file
cat $AT | python ./tool/tool-createPBdata.py S.txt



####### make F(answer)
python ./tool/tool-kameimap.py $M $T $AT F_answer.txt



####### utility
for utility in E1-ItemCF-s.py E2-ItemCF-r.py E3-topk.py E4-diff-date.py E5-diff-price.py E6-nrow.py
do
  ruby ./tool/tool-ncat.rb $M $T $AT | python "./utility/"$utility
done



####### security
### python
for security_py in S1-datenum.py S2-itemprice_sub.py S3-itemnum_sub.py S4-itemdate_sub.py
do
  echo $security_py
  for ratio in 25 50 75 100
  do
    echo $ratio
    ruby ./tool/tool-ncat.rb $M S.txt "./given_data/T"$ratio".txt" | python "./reidentify/"$security_py > "Fh"$ratio"_tmp.txt"
    python ./tool/tool-compare_and.py F_answer.txt "Fh"$ratio"_tmp.txt"
    rm -f *_tmp.txt *_tmp.csv
  done
done

### ruby
for security_rb in S5-item2pricenum.rb S6-item2datenum.rb
do
  echo $security_rb
  for ratio in 25 50 75 100
  do
    echo $ratio
    ruby ./tool/tool-ncat.rb $M S.txt "./given_data/T"$ratio".txt"  | ruby "./reidentify/"$security_rb > "Fh"$ratio"_tmp.txt"
    python ./tool/tool-compare_and.py F_answer.txt "Fh"$ratio"_tmp.txt"
    rm -f *_tmp.txt *_tmp.csv
  done
done



####### reidentify by user
echo "reidentification by user"
echo "25"
python ./tool/tool-compare_and.py F_answer.txt $Fh25_user
echo "50"
python ./tool/tool-compare_and.py F_answer.txt $Fh50_user
echo "75"
python ./tool/tool-compare_and.py F_answer.txt $Fh75_user
echo "100"
python ./tool/tool-compare_and.py F_answer.txt $Fh100_user
