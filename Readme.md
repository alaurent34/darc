# DARC - Data Anonymisation and Re-indentification Competition

This Repository contains all source code for PETS Competition DARC. More
specifically it contains :
  - Source code for the re-identification metrics.
  - Source code for the utility metric.
  - Source code for succes in re-identification.

What need to be done :
  1. Create a script to sample the data from UCI.
  2. Document source code available
  3. Translate japaneese comments in source code
  4. *Any suggestion goes here*

## Datasets

### Source
Original dataset is from UCI and can be downloaded
[here](https://archive.ics.uci.edu/ml/datasets/Online+Retail).

### Description

**Original** :
This is a transnational data set which contains all the transactions occurring
between 01/12/2010 and 09/12/2011 for a UK-based and registered non-store online
retail.The company mainly sells unique all-occasion gifts. Many customers of the
company are wholesalers. [1](https://archive.ics.uci.edu/ml/datasets/Online+Retail)

**PWSCup** :
The dataset is separated in two distinct datasets, one which contain all `n`
clients (`M`) and the other containing all transactions made by those `n`
clients during one year (`T`).

## Notations

You can find in the table beloe all the notation used in the scripts and this
Readme.

  <table class="tg">
    <tr>
      <th class="tg-us36">Notations</th>
      <th class="tg-us36">Meaning</th>
    </tr>
    <tr>
      <td class="tg-us36">M</td>
      <td class="tg-us36">dataset containing all `n` clients.</td>
    </tr>
    <tr>
      <td class="tg-us36">T</td>
      <td class="tg-us36">Dataset containing all transaction of M's clients.</td>
    </tr>
    <tr>
      <td class="tg-us36">`T_a`</td>
      <td class="tg-us36">Dataset containing `a%` of T transactions.</td>
    </tr>
    <tr>
      <td class="tg-us36">A(T)</td>
      <td class="tg-us36">Anomyzed version of T.</td>
    </tr>
    <tr>
      <td class="tg-us36">S</td>
      <td class="tg-us36">A(T) with row shuffled</td>
    </tr>
    <tr>
      <td class="tg-us36">F</td>
      <td class="tg-us36">Mapping table between orginal ID (in `M`) and
      anonymized ID (in A(T))</td>
    </tr>
    <tr>
      <td class="tg-us36">F hat</td>
      <td class="tg-us36">Guess Mapping table by the adversary</td>
    </tr>
    <tr>
      <td class="tg-us36">R</td>
      <td class="tg-us36">Correspondance between ID and Pseudo in S and A</td>
    </tr>
    <tr>
      <td class="tg-us36">P</td>
      <td class="tg-us36">Correspondance between line shuffle in S and A(T)</td>
    </tr>
    <tr>
      <td class="tg-us36">J(X,Y)</td>
      <td class="tg-us36">Concatenation of file X and Y</td>
    </tr>
  </table>


## Metrics
### <a name="security"></a>Re-identification metrics

>  TODO: Description sommaire des métriques de ré-identification <17-04-18, Antoine> >

  There is 6 re-indentification metrics, which are :
  <table class="tg">
    <tr>
      <th class="tg-us36">Metrics name</th>

      <th class="tg-us36">Purpose</th>

    </tr>
    <tr>
      <td class="tg-us36">S1</td>
      <td class="tg-us36">Try to reconstruct F_h by comparing Purchase Date and<br>
      Quantity in T_a and S</td>
    </tr>
    <tr>
      <td class="tg-us36">S2</td>
      <td class="tg-us36">Try to reconstruct F_h by comparing ID item and Unit<br>
      price in T_a and S</td>
    </tr>
    <tr>
      <td class="tg-us36">S3</td>
      <td class="tg-us36">Try to reconstruct F_H by comparing (egality) ID item<br>
      and quantity</td>
    </tr>
    <tr>
      <td class="tg-us36">S4</td>
      <td class="tg-us36">Try to reconstruct F_h by comparing (egality) ID item<br>
      and Purchase Date</td>
    </tr>
    <tr>
      <td class="tg-us36">S5</td>
      <td class="tg-us36">Try to reconstruct F_h by comparing (egality) the<br>
      first two digit of the ID item, quantity and price</td>
    </tr>
    <tr>
      <td class="tg-us36">S6</td>
      <td class="tg-us36">Try to reconstruct F_h by comparing (egality) the<br>
      first two digit of the ID item, Purchased Date and price</td>
    </tr>
  </table>

### <a name="utility"></a>Utility metrics

>  TODO: Description sommaire des métriques d'utilité <17-04-18, Antoine> >

There is 6 utility metrics, which are :

  <table class="tg">
    <tr>
      <th class="tg-us36">Metrics name</th>
      <th class="tg-us36">Purpose</th>
    </tr>
    <tr>
      <td class="tg-us36">E1</td>
      <td class="tg-us36">Construct a similarity matrix of item buyed (User that<br>
      have bought this item also bought item_i). Here the score is maximized if<br>
      the quantity is high (calculated by dozen). We calculate the difference<br>
      between the two matrix of item buyed as a score.</td>
    </tr>
    <tr>
      <td class="tg-us36">E2</td>
      <td class="tg-us36">Idem than E1 but here but only for item with a<br>
      quantity <= 11.</td>
    </tr>
    <tr>
      <td class="tg-us36">E3</td>
      <td class="tg-us36">Difference and similarity matrix between top-`k` items<br>
      bought</td>
    </tr>
    <tr>
      <td class="tg-us36">E4</td>

      <td class="tg-us36">Calculate the mean distance in day between <br>
      anonymised and ground truth trajectories.</td>

    </tr>
    <tr>
      <td class="tg-us36">E5</td>

      <td class="tg-us36">Calculate the difference, as the ratio, of all item prices</td>

    </tr>
    <tr>
      <td class="tg-us36">E6</td>

      <td class="tg-us36">Calculate the ration between the number of lines <br>
      removed in the anonymized table over the number of lines in the original dataset.</td>

    </tr>
  </table>

### Success metrics

>  TODO: Description sommaire des métriques de succès <17-04-18, Antoine> >

# List of programs

Here we discuss of the purpose of the differents scripts found in [PWSCup 2017
archive](https://pwscup.personal-data.biz/web/pws2017/data/PWSCUP2017_Samples.zip).

We will not represent here scripts for Utility and Metrics as we already list
them above.

## To sort

This is the current list of script to sort. Please update this list once the
script is sorted. Programs can be found under ADD PATH HERE.

### Python

*Done*

### Ruby

 - tool-eval-re-tcm.rb
 - tool-map.rb
 - tool-ncat.rb
 - tool-nsplit.rb
 - tool-r2cid.rb

### R

Just some re-identification code

### Feelings

For now i have the feeling that we can only use python scripts for our needs.

## Sorted

This is a list of script sorted by categories and with an explaination of what
it does.

Thanks to respect the following format when placing a script here.

Format : - scipt.ext : Explaination

   | Input | Way | Outuput | Way |
   | ---   | --- | ---     | --- |
   | X     | Y   | Z       | V   |

   *Example*:
   ```
   python ./example.py
   ```
*NB : Some remarks*

#### Concatenation scripts

There is two scripts for concatening files are :

 - tool-ncat.py, tool-ncat.rb : They are usualy used to concat M, A and AT and
   return a J file.

   | Input                         | Way   | Outuput   | Way    |
   | ---                           | ---   | ---       | ---    |
   | J(M,T,AT) and Result_name.csv | stdin | J(M,T,AT) | stdout |

   *Example*:
   ```
   python ./tool-ncat.py M_sample.csv T_sample.csv AT_sample.csv > J_out.csv
   ```

*NB : Also i suggest we use the python one to need only one interpreter instead
of two.*

### Creation scripts

 - tool-createPBdata.py : This script take AT, the player anonymised database
   and create the file S with 'DEL' entry supress and line shuffled and P (or
   just S with the version inside ./drill).

   | Input | Way   | Outuput | Way         |
   | ---   | ---   | ---     | ---         |
   | A(T)  | stdin | S       | args (path) |

   *Example*:
   ```
   cat AT.csv | python ./tool-createPBdata.py S.csv
   ```

 - tool-kamei.py : The script take a T file and generate A(T), S, R and P. It
   play the role of an participant.

   | Input | Way         | Outuput       | Way                    |
   | ---   | ---         | ---           | ---                    |
   | T     | args (path) | A(T), S, R, P | file generated by prog |

   *Example*:
   ```
   python ./tool-kamei.py T.csv
   ```

 - tool-kameimap.py : Take M, T, and A(T) and create F, the correspondance
   between ID and Pseudo for each month.

   | Input  | Way         | Outuput | Way         |
   | ---    | ---         | ---     | ---         |
   | M,T,AT | args (path) | F  | args (path) |

   *Example*:
   ```
   python ./tool-kameimap.py $M $T $AT F.txt
   ```

 - tool-divide.py : Take M, A, AT in stdin and outpout the 3 files separated.

   | Input                         | Way   | Outuput | Way                         |
   | ---                           | ---   | ---     | ---                         |
   | J(M,T,AT) and Result_name.csv | stdin | M,T,AT  | file generated (X_name.csv) |

   *Example*:
   ```
   python ./tool-ncat.py M_sample.csv T_sample.csv AT_sample.csv | python ./tool-devide.py Result_sample_test.csv
   ```

### Scoring

#### Comparing Two F files

 - tool-compare_and.py : Take F, F_hat and give the re-identification ration.
 - tool-mapcompare.py : Idem
<<<<<<< HEAD

   | Input    | Way         | Outuput                 | Way    |
   | ---      | ---         | ---                     | ---    |
   | F, F_hat | args (path) | re-identification ratio | stdout |

   *Example*:
   ```
   python ./tool-compare_and.py F.csv F_hat.csv
   ```

=======

   | Input    | Way         | Outuput                 | Way    |
   | ---      | ---         | ---                     | ---    |
   | F, F_hat | args (path) | re-identification ratio | stdout |

   *Example*:
   ```
   python ./tool-compare_and.py F.csv F_hat.csv
   ```

>>>>>>> antoine
There is also a file which take J(R,P) and J(R',P') and give the re-identification rate:

 - tool-compare.py

In my experience only tool-compare_and.py need to be used for the
re-identification phases, the two other are juste simple copy.

#### Utility metric scripts

All scripts E_i calculate a utility measure that is explain in the subection
[here](#utility). They have the following characteristics :

   | Input    | Way   | Outuput       | Way    |
   | ---      | ---   | ---           | ---    |
   | J(M,A,T) | stdin | utility ratio | stdout |

   *Example*:
   ```
   python ./tool-ncat.py M.csv T.csv AT.csv | python ./E1-ItemCF-s.py
   ```

#### Security metric scripts

All scripts S_i calculate a security measure that is explain in the subsection [here](#security).
They have the following characteristics :

   | Input    | Way   | Outuput       | Way    |
   | ---      | ---   | ---           | ---    |
   | J(M,S,`T_a`) | stdin | `F_h` | stdout |

   *Example*:
   ```
   python ./tool-ncat.py M.csv S.csv `T_a`.csv | python ./S1-datenum.py > `F_h_a.csv`
   ```

### Misc

 - common.py : Read input and write output R. Used in Secutiry and Utility
   metrics.

# TO DO

- Script to check file format for better description of the error AND security.
- Metrics need to return their values and not print them.
