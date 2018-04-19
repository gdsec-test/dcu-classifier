DCU Classifier

Takes in classify/scan/fingerprint requests from the DCU Auto Abuse API in order to process requests asynchronously.

## Cloning
To clone the repo, use git, and set up a python virtual env project:

```
mkproject dcu-classifier
git clone git@github.secureserver.net:ITSecurity/dcu-classifier.git
cd dcu-classifier
```

## Installing Dependencies
Install private pips and main project dependencies:

```
pip install -r private_pips.txt
pip install -r requirements.txt

If you also wish to run test suites, install the test dependencies:

pip install -r test_requirements.txt
```

## Building
This section is pending the creation of docker files

## Deploying
This section is pending the creation of docker files

## Testing
To run all tests, run the following from within the tests/ directory

```
nosetests --with-coverage --cover-package=service
```

## Built With
This project utilizes Celery and Python

## Running Locally

If you would like to run this locally, you will need to specify the following environment variables:

1. `sysenv` (dev, ote, prod)
2. `DB_PASS` (Password for MongoDB)
3. `BROKER_PASS` (Password for Celery)
4. `WORKER_MODE` (needs to be `classify` or `scan`)

You may also need to configure settings.py and celeryconfig.py to specify additional MongoDB and Celery settings.

DCU Classifier can then be run locally by running `celery -A run worker -l INFO --without-gossip --without-heartbeat --without-mingle`