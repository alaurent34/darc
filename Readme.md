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

  There is 6 re-indentification metrics, which are :
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
      <td class="tg-us36"></td>
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

## To sort

## Sorted

### Category 1

### Category 2

### ...
