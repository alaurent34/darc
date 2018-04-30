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
### Re-identification metrics

>  TODO: Description sommaire des métriques de ré-identification <17-04-18, Antoine> >

  There is 6 re-indentification metrics, which are :
  <table class="tg">
    <tr>
      <th class="tg-us36">Metrics name</th>
      <th class="tg-us36">Purpose</th>
    </tr>
    <tr>
      <td class="tg-us36">S1</td>
      <td class="tg-us36"></td>
    </tr>
    <tr>
      <td class="tg-us36">S2</td>
      <td class="tg-us36"></td>
    </tr>
    <tr>
      <td class="tg-us36">S3</td>
      <td class="tg-us36"></td>
    </tr>
    <tr>
      <td class="tg-us36">S4</td>
      <td class="tg-us36"></td>
    </tr>
    <tr>
      <td class="tg-us36">S5</td>
      <td class="tg-us36"></td>
    </tr>
    <tr>
      <td class="tg-us36">S6</td>
      <td class="tg-us36"></td>
    </tr>
  </table>

### Utility metrics

>  TODO: Description sommaire des métriques d'utilité <17-04-18, Antoine> >

There is 6 utility metrics, which are :

  <table class="tg">
    <tr>
      <th class="tg-us36">Metrics name</th>
      <th class="tg-us36">Purpose</th>
    </tr>
    <tr>
      <td class="tg-us36">E1</td>
      <td class="tg-us36">Construct a similarity matrice</td>
    </tr>
    <tr>
      <td class="tg-us36">E2</td>
      <td class="tg-us36"></td>
    </tr>
    <tr>
      <td class="tg-us36">E3</td>
      <td class="tg-us36"></td>
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
*NB : Some remarks*

### Creation scripts

 - tool-createPBdata.py : This script take AT, the player anonymised database
   and create the file S with 'DEL' entry supress and line shuffled and P (or
   just S with the version inside ./drill).

 - tool-kamei.py : The script take a T file and generate A(T), S, R and P. It
   play the role of an participant.

 - tool-kameimap.py : Take M, T, and A(T) and create F, the correspondance
   between ID and Pseudo for each month.

 - tool-divide.py : Take M, A, AT in stdin and outpout the 3 files separated.

#### Concatenation scripts

There is two scripts for concatening files are :

 - tool-ncat.py, tool-ncat.rb : They are usualy used to concat M, A and AT and
   return a J file.

*NB : Also i suggest we use the python one to need only one interpreter instead
of two.*

### Scoring

For scoring mesure there is multiples files :
 - Scripts for utility and security measure (Ei and Si)

Those to compare F and F_hat:
 - tool-compare_and.py
 - tool-mapcompare.py

And this one take J(R,P) and J(R',P') to give the re-identification rate:
 - tool-compare.py

In my experience only tool-mapcompare.py need to be used for the
re-identification phases, the two other are juste simple copy.

*NB: Author seems to use tool-compare_and.py*

### Misc

 - common.py : Read input and write output R.

Usefull when you want to pipe result for exemple : tool-ncat.py A B C | E1.py
