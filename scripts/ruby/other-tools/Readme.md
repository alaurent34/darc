# Description of ruby scripts by authors
## Data definition

- M.csv  : Master data.
- T.csv  : Transaction data.
- AT.csv : The same row number of T. "DEL" line is about 50%, and ID is Pseudonym ID (incomplete encryption).
- S      : Permuted Anonymized data without "DEL".
- R      : Correspondence list of Real ID.
- P      : Permuted row number of A(T) -> S.
- F      : ID Map
- Fhat   : Pseudonym ID Map

## Scripts

### tool-ncat.py
- Author  : Koki Hamada
- Function: create J file
- Command :
    ```
    ruby tool-ncat.rb File1 File2 File3 > File123
    ```

### tool-nsplit.rb
- Author  : Koki Hamada
- Function: split J file
- Command :
    ```
    ruby tool-nsplit.rb File1 File2 File3 < File123
    ```

### tool-r2cid.rb
- Author  : Koki Hamada
- Function: J(M, R) -> J(cid(R))
- Command :
    ```
    cat J_****.txt | ruby S1-random.ruby | ruby tool-r2cid.rb
    ```

### tool-map.rb
- Author  : Koki Hamada
- Function: M, T, AT -> F (Fhat)
- Command :
    ```
    ruby tool-ncat.rb M_***.txt T_***.txt AT_***.txt | ruby tool-map.rb > map_***.txt
    ```
