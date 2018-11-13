# DARC - Data Anonymisation and Re-identification Competition

This Repository contains all source code for PETS Competition: DARC. More
specifically it contains:

- Sampled data from UCI for DARC (ground truth).
- Original data from UCI.
- T-sne representation of the sampled dataset.
- Source code for the re-identification metrics.
- Source code for the utility metric.
- Source code for success for players re-identification.
- Source code for the integration of metrics in CrowdAI plateform

What need to be done:

1. The integration of the code in the [CrowdAI evaluator][crowd-eval] to
   automatize the phases procedure (Mostly done).
2. Amelioration of the functions which check the file format submitted by the
   participants for each phases, they also provide detailed informations to
   participants about formatting errors in the file submitted.
3. Performing some tests to make sure the competition will run as smoothly as
   possible.
4. *Any suggestion goes here*

[crowd-eval]: https://github.com/crowdAI/crowdai-example-evaluator

## Datasets

### Source

Original dataset is from UCI and can be downloaded [here][trans-dataset].

### Description

**Original**

[This][trans-dataset] is a transactional dataset which contains all the
transactions that have occurred between 01/12/2010 and 09/12/2011 for a UK-based
and registered non-store online retail. The company mainly sells unique
all-occasion gifts. Many customers of the company are wholesalers.

[trans-dataset]: https://archive.ics.uci.edu/ml/datasets/Online+Retail

**PWSCup**

The dataset is separated in two distinct datasets, one which contain all $`n`$
clients ($`M`$) and the other containing all transactions made by those $`n`$
clients during one year ($`T`$).

## Notations

You can find in the table below all the notations used in the scripts and this
Readme.

  <table class="tg">
    <tr>
      <th class="tg-us36">Notations</th>
      <th class="tg-us36">Meaning</th>
    </tr>
    <tr>
      <td class="tg-us36">$`M`$</td>
      <td class="tg-us36">dataset containing all $`n`$ clients.</td>
    </tr>
    <tr>
      <td class="tg-us36">$`T`$</td>
      <td class="tg-us36">Dataset containing all transaction of $`M`$'s clients.</td>
    </tr>
    <tr>
      <td class="tg-us36">$`T_a`$</td>
      <td class="tg-us36">Dataset containing $`a|T|`$ transactions. With $`a \in \{.25, .50, .75\}`$</td>
    </tr>
    <tr>
      <td class="tg-us36">$`A(T)`$</td>
      <td class="tg-us36">Anomyzed version of $`T`$.</td>
    </tr>
    <tr>
      <td class="tg-us36">$`S`$</td>
      <td class="tg-us36">$`A(T)`$ with row shuffled</td>
    </tr>
    <tr>
      <td class="tg-us36">$`F`$</td>
      <td class="tg-us36">Mapping table between orginal ID (in $`M`$) and
      anonymized ID (in $`A(T)`$): it's a generated File</td>
    </tr>
    <tr>
      <td class="tg-us36">$`F`$ hat</td>
      <td class="tg-us36">Guess Mapping table by the adversary: Generated File</td>
    </tr>
    <tr>
      <td class="tg-us36">$`R`$</td>
      <td class="tg-us36">Correspondance between ID and Pseudo in $`S`$ and $`A`$</td>
    </tr>
    <tr>
      <td class="tg-us36">$`P`$</td>
      <td class="tg-us36">Correspondance between line shuffle in $`S`$ and $`A(T)`$</td>
    </tr>
    <tr>
      <td class="tg-us36">$`J(X,Y)`$</td>
      <td class="tg-us36">Concatenation of file $`X`$ and $`Y`$</td>
    </tr>
  </table>

## Metrics

### Re-identification metrics

There is 6 re-indentification metrics (all the comparaison done here are
eguality comparision), which are:

  <table class="tg">
    <tr>
      <th class="tg-us36">Metrics name</th>
      <th class="tg-us36">Purpose</th>
    </tr>
    <tr>
      <td class="tg-us36">$`S_1`$</td>
      <td class="tg-us36">Try to reconstruct $`F_h`$ by comparing Purchase Date and
      Quantity in $`T_a`$ and $`S`$</td>
    </tr>
    <tr>
      <td class="tg-us36">$`S_2`$</td>
      <td class="tg-us36">Try to reconstruct $`F_h`$ by comparing ID item and Unit
      price in $`T_a`$ and $`S`$</td>
    </tr>
    <tr>
      <td class="tg-us36">$`S_3`$</td>
      <td class="tg-us36">Try to reconstruct $`F_H`$ by comparing (egality) ID item
      and quantity</td>
    </tr>
    <tr>
      <td class="tg-us36">$`S_4`$</td>
      <td class="tg-us36">Try to reconstruct $`F_h`$ by comparing (egality) ID item
      and Purchase Date</td>
    </tr>
    <tr>
      <td class="tg-us36">$`S_5`$</td>
      <td class="tg-us36">Try to reconstruct $`F_h`$ by comparing (egality) the
      first two digit of the ID item, quantity and price</td>
    </tr>
    <tr>
      <td class="tg-us36">$`S_6`$</td>
      <td class="tg-us36">Try to reconstruct $`F_h`$ by comparing (egality) the
      first two digit of the ID item, Purchased Date and price</td>
    </tr>
  </table>

### Utility metrics

There is 6 utility metrics, which are:

  <table class="tg">
    <tr>
      <th class="tg-us36">Metrics name</th>
      <th class="tg-us36">Purpose</th>
    </tr>
    <tr>
      <td class="tg-us36">$`E_1`$</td>
      <td class="tg-us36">Construct a similarity matrix of item buyed (User that
      have bought this item also bought item_i). Here the score is maximized if
      the quantity is high (calculated by dozen). We calculate the difference
      between the two matrix of item buyed as a score.
      <br> More precisly we construct two matrix $`M_1`$ and $`M_2`$, one for the
      original dataset and one for the anonymised one. Both are of size $`n \times
      n`$ where $`n`$ is the number of item. For $`M_{ij}`$ represent the number
      of people who have bought the item i and have also bought the item
      $`j`$.<br>
      This procede is called a [collaborative filtering][collab-filtering].
      </td>
    </tr>
    <tr>
      <td class="tg-us36">$`E_2`$</td>
      <td class="tg-us36">Idem than $`E_1`$ but here but only for item with a
      quantity $`\le 11`$.</td>
    </tr>
    <tr>
      <td class="tg-us36">$`E_3`$</td>
      <td class="tg-us36">Caluclate the difference (as in set difference) and similarity matrix between top-$`k`$ items
      bought from ground truth and anonymised dataset.</td>
    </tr>
    <tr>
      <td class="tg-us36">$`E_4`$</td>
      <td class="tg-us36">Calculate the mean distance in day between
      anonymised and ground truth transactions.</td>
    </tr>
    <tr>
      <td class="tg-us36">$`E_5`$</td>
      <td class="tg-us36">Calculate the difference, as the ratio, of all item prices</td>
    </tr>
    <tr>
      <td class="tg-us36">$`E_6`$</td>
      <td class="tg-us36">Calculate the ratio between the number of lines
      removed in the anonymized table over the number of lines in the original dataset.</td>
    </tr>
  </table>

[collab-filtering]: https://en.wikipedia.org/wiki/Collaborative_filtering

### Success metrics

To calculate the score of re-identification, the two F files from the ground
truth and the attacker are compared. For a participant to make a point it have
to guess all the pseudonyms for one person (*i.e.*, for all month guess if it is DEL
or a pseudonym). One error occurs a 0 in the count for the line.

Then the count of points are divided by the number of line (persons) in the F
file.

## Information about PWSCup 2017

<!-- TODO:  Explain a bit about PWSCup Here <21-05-18, Antoine Laurent> > -->

For more informations about PWSCup 2017, you can visit this [site][pws] for now
(you can use Google Translate to translate the website on Chrome browser).

[pws]: https://pwscup.personal-data.biz/web/pws2017/info.php

# How to use

We describe here how you can test the scripts written.

## Requirements

**You need python3.6**

First, install the requirements on your system using the `pip3` python package
manager.

```sh
pip3 install --requirements=requirements.txt
```

## CrowdAI evaluator

To use the CrowdAI DARC evaluator, execute `darc_evaluator.py` as follows:

```sh
python darc_evaluator.py
```

**Round 1**

For testing with your own submission, in `main.py` you have to change the line

```python
_client_payload["submission_file_path"] = "data/submission.csv"
```

with the path of your file.

This will create a submission as: `AT_*YourTeamName*_*AttemptNumber*.csv`. For
testing you need to format the name of your submission like said above, in order
for `compute_all_f_orig` to run without error. During the competition AT files
will be saved with this naming automatically.

**Round 2**

In `utils.py`, the function with the following signature generates all of the
*F_files* of your submission:

```python
compute_all_f_orig(folder_path, ground_truth_file_path)
```

Then you just have to enter the path of your files and the name and attempt nb
you want to attack in the respective entries of the dictionnary as showed in the
following:

```python
# Submission file
_client_payload["submission_file_path"]

# Attacked team
_context["team_attacked"]

# The number of attempts
_context["attempt_attacked"]
```

**NB**: In `utils.py` you'll also have to enter all the information about your
redis storage.

## Metrics testing

If you want to test the metrics alone you can do it by executing the python file
`metrics.py`:

```
python metrics.py
```

**NB**: For the scripts to be working you need to use a python version above
3.6.

# Description of files

**`Metrics.py`**

This module serves the purpose of calculating the metrics used in the 1st phase.
You can find the UtilityMetrics class, the ReidentificationMetrics class and a
CollaborativeFiltering class. This last one is used in the utility metrics for
metrics $`E_1`$, $`E_2`$ and $`E_3`$.

An example of how to use this module is given in a `main()` function.

**`Utils.py`**

This file serves the purpose of stocking some configuration and function that
will be used in both phase and are not considered as metrics. For example you
can found a variable $`T_{COL}`$ that store the name of the columns you want to use
for your ground truth DataFrame.

Also you can find the method to compare two F files, which is useful in both
phase and is not a metric itself.

**`Preprocessing.py`**

This file serve the purpose of reading and embbeding the files needed for the
DARC competition, as submission and ground truth files for example. It's used by
`darc_evaluator.py`

**`Darc_evaluator.py`**

This file serve the purpose of integrating the process of the competition in the
CrowdAI platform.

