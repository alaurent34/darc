# DARC - Data Anonymisation and Re-identification Competition

This is a python application of DARC. DARC is a competition held at PETs on the
AIcrowd plateform. To participate please go on AIcrowd
[website](https://www.aicrowd.com/challenges/data-anonymization-and-re-identification-competition-darc).

## Getting Started

These instructions will get you a copy of the project up and running on your
local machine for development and testing purposes. See deployment for notes on
how to deploy the project on a live system.

### Prerequisites

In order to run the tests and to test your submission you need to do the following:

**If you want to use DARC core**:

- [python3.6](https://www.python.org/downloads/release/python-366/) or **higher**
- [pip](https://pip.pypa.io/en/stable/)

**If you only want to test it with docker**:

- [docker](https://docs.docker.com/get-started/) and docker-compose

On linux you can use your package manager to intall them as below
```bash
#Ubuntu
apt-get install docker

#Arch-Linux
sudo pacman -S docker
```

### Installing

Install the requirements via pip:

```bash
pip install -r requirements.txt
```

## Running the tests

To run the test on the core execute the following command:

```bash
docker-compose up --build --remove-orphans --renew-anon-volumes --abort-on-container-exit test
```

It will run test to check if the current version of the DARC core and the older
one behaves in the same way. To check the result consult the file
`./data/testing_files/testing.log`

**TODO : Make some unit test to check the methods**


To test if the platform (darc\_evaluator) is working do:

```bash
docker-compose up --build --remove-orphans --renew-anon-volumes --abort-on-container-exit darc
```

To set the path of the submission for both round 1 and 2 during the test of
the platefrom, change the following variables in `config.py`:

```python
class Config()

#...

R1_SUBMISSION_FILE = "data/example_files/submission_DEL.csv"
R2_SUBMISSION_FILE = "./data/example_files/F_a_attempt_2.tar"
```

## Usage of the DARC core

To use the DARC core just import it in your project as :

```python
import darc_core
from darc_core.preprocessing import round1_preprocessing
from darc_core.utils import check_format_trans_file

# Read database from files
ground_truth, submission = round1_preprocessing(
    self.answer_file_path, submission_file_path
)

# Check the format of the Anonymized Transaction file
check_format_trans_file(ground_truth, submission)

# Run metrics for a submission (AT)
metric = darc_core.Metrics(ground_truth, submission)
scores = metric.scores()
```

## Contributing

Please free to contributing in the darc\_core code. Espetially in term of
optimization or architecture model.

## Authors

All the persons below have participated to DARC implementation and deployements

* **Antoine Laurent** - [Ph.D candidate at UQAM](mailto:laurent.antoine@courrier.uqam.ca)
* **Sébastien Gambs** - [Professor at UQAM](mailto:gambs.sebastien@uqam.ca)
* **Louis Béziaud** - [Ph.D candidate at UQAM](mailto:laurent.antoine@courrier.uqam.ca)
* **Sharada Mohanty** - [CEO & Co-funder of AIcrowd](mailto:sharada.mohanty@epfl.ch)
* **Yoann Pagnoux** - [Master Student at INSA](mailto:yoann.pagnoux@insa-cvl.fr)

And of course all the people from the comite.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* We would like to thank all our colleagues, previous trainees and students who
  gave their time and energy for the competition test.
