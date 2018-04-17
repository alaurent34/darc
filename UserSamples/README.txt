### READ_ME ###



### DEFINITION ###
M          : Master data
T          : Transaction data
AT         : Anonymized Transaction data (same row number to T, and include 'DEL')
S          : Anonymized Transaction data (random row number without 'DEL')
R          : Correspondence list of Real ID.
P          : Permuted row number of A(T) -> S.
J(M, T, AT): Jointed data (M, T, and AT,  the first row is amount of the lines of each data)
J(M, S, T) : Jointed data (M, S, and T,  the first row is amount of the lines of each data)
f          : Pseudonym list
f-hat      : Estimated pseudonym list


#################### S1 ####################
Algorithm: S1-datenum.py, common.py
Author: Ryo Nojima
Import: J(M, S, T)
Export: f-hat
Command: cat J_****.txt | python S1-datenum.py


#################### S2 ####################
Algorithm: S2-itemprice.py, common.py
Author: Ryo Nojima
Import: J(M, S, T)
Export: f-hat
Command: cat J_****.txt | python S2-itemprice.py


#################### S3 ####################
Algorithm: S3-itemnum.py, common.py
Author: Ryo Nojima
Import: J(M, S, T)
Export: f-hat
Command: cat J_****.txt | python S3-itemnum.py


#################### S4 ####################
Algorithm: S4-itemdate.py, common.py
Author: Ryo Nojima
Import: J(M, S, T)
Export: f-hat
Command: cat J_****.txt | python S4-itemdate.py



#################### E1 ####################
Algorithm: E1-ItemCF-s.py
Author: Takao Murakami, Masanori Monda
Import: J(M, T, AT)
Export: Utility score
Command: cat J_****.txt | python E1-ItemCF-s.py


#################### E2 ####################
Algorithm: E2-ItemCF-r.py
Author: Takao Murakami, Masanori Monda
Import: J(M, T, AT)
Export: Utility score
Command: cat J_****.txt | python E2-ItemCF-r.py


#################### E3 ####################
Algorithm: E3-topk.py
Author: Takao Murakami, Masanori Monda
Import: J(M, T, AT)
Export: Utility score
Command: cat J_****.txt | python E3-topk.py


#################### E4 保留 ####################
Algorithm: E4-trans-diff.py, common.py
Author: Ryo Nojima
Import: J(M, T, AT)
Export: Utility score
Command: cat J_****.txt | python E4-trans-diff.py


#################### E5 ####################
Algorithm: E5-ham.ruby
Author: Koki Hamada
Import: J(M, T, AT)
Export: Utility score
Command: cat J_****.txt | ruby E5-ham.ruby


#################### E6 ####################
Algorithm: E6-nrow.py
Author: Hidenobu Oguri
Import: J(M, T, AT)
Export: Utility score
Command: cat J_****.txt | python E6-nrow.py




### Release Note ###

Ver 1.2:
Utility E3-topk.py : Small bug fixed, change output comment. (2017/09/14) 

Ver 1.1:
Reidentify S1-S4 : Small bug fixed (2017/09/13) 

Ver 1.0:
Released (2017/09/11) 


