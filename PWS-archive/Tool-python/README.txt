
#### Data definition ####

M.csv  : Master data.
T.csv  : Transaction data.
AT.csv : The same row number of T. "DEL" line is about 50%, and ID is Pseudonym ID (incomplete encryption). 
S      : Permuted Anonymized data without "DEL".
R      : Correspondence list of Real ID.
P      : Permuted row number of A(T) -> S.
Fhat   : Pseudonym ID Map




#################### tool-ncat.py ####################
Author  : Hidenobu Oguri
Command : python tool-ncat.py M.csv T.csv AT.csv  >  J50.txt

Function: To make a Joint File. e.g., J( M, T, A(T) )
	J50.txt = J(M, T, A(T))
	"J()" file format is the standard of this system.(input or output)




#################### tool-kamei.py ####################
Author  : Hidenobu Oguri
Command : python tool-kamei.py T75.csv
			-> output: AT_**.csv
			-> output: S_**.csv
			-> output: P_**.csv
			-> output: R_**.csv

Function:  To change the IDs into Pseudonym IDs on A(T).

		if you change the "Pseudonym IDs (you can check the result)" into "Encrypt IDs (cannot check)", See the below lines.

		## Pseudonym IDs
		PsuID =  str( str( TRANS_MARK[0][i] ) + str(DIV_APPEND[DIV_CODE]) )
		## Encrypt IDs (MD5)
		#PsuID = hashlib.md5( str( str( TRANS_MARK[0][i] ) + str(DIV_APPEND[DIV_CODE]) ).encode('utf-8') ).hexdigest()


## Pseudonym IDs Sample

 ID      Pseudonym IDs
 14911   K14911NO
 14911   K14911NO
 14911   K14911NO
   DEL        DEL
   DEL        DEL
 17288   K17288NO
 17288   K17288NO
 17288   K17288NO

## Encrypt IDs Sample

    ID                        Encrypt IDs
 14911  Kdf81417c164643bcc324f57c4a25424d
 14911  Kdf81417c164643bcc324f57c4a25424d
 14911  Kdf81417c164643bcc324f57c4a25424d
   DEL                                DEL
   DEL                                DEL
 17288  K6ca98cface01821d439fd7f5d8029d75
 17288  K6ca98cface01821d439fd7f5d8029d75
 17288  K6ca98cface01821d439fd7f5d8029d75





#################### tool-kameimap.py ####################
Author  : Hidenobu Oguri
Command : python tool-kameimap.py  M.csv T.csv AT_**.csv (made by tool-kamei.py)
		-> output: Fh_**.csv

Function: To make a Fhat = "Pseudonym ID Map"

ID,12,1,2,3,4,5,6,7,8,9,10,11
12352,DEL,B12352FE,C12352MA,DEL,DEL,DEL,DEL,DEL,I12352SE,DEL,K12352NO,DEL
12356,A12356JA,DEL,DEL,D12356AP,DEL,DEL,DEL,DEL,DEL,DEL,K12356NO,DEL
12364,DEL,DEL,DEL,DEL,DEL,DEL,DEL,H12364AU,I12364SE,J12364OC,DEL,DEL
12378,DEL,DEL,DEL,DEL,DEL,DEL,DEL,H12378AU,DEL,DEL,DEL,DEL





#################### tool-mapcompare.py ####################
Author  : Hidenobu Oguri
Command : python tool-mapcompare.py  F.csv  Fh.csv

Function: Read "MAP1","MAP2"  files, and calculate the Match rate (= Re-Identify rate 1).







