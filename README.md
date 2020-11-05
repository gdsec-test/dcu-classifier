# DCU Classifier

Takes in classify/scan requests from the DCU Auto Abuse API in order to process requests asynchronously.

### dcu-classifier
This service is used to determine a fraud_score given a url, using the ML API predict/dcu_fraud_html endpoint.

### dcu-scanner
This service is used to determine a fraud_score given a url, using the ML API predict/dcu_fraud_html endpoint.  If the fraud score exceeds a specified threshold, it will submit a ticket to the Abuse API

## Cloning
To clone the repository via SSH perform the following
```
git clone git@github.secureserver.net:digital-crimes/dcu-classifier.git
```

It is recommended that you clone this project into a pyvirtualenv or equivalent virtual environment.

## Installing Dependencies
To install all dependencies for development and testing simply run `make`.

## Building
Building a local Docker image for the respective development environments can be achieved by
```
make [dev, ote, prod]
```

## Deploying
Deploying the Docker image to Kubernetes can be achieved via
```
make [dev, ote, prod]-deploy
```
You must also ensure you have the proper push permissions to Artifactory or you may experience a `Forbidden` message.

## Testing
```
make test     # runs all unit tests
make testcov  # runs tests with coverage
```

## Style and Standards
All deploys must pass Flake8 linting and all unit tests which are baked into the [Makefile](Makfile).

There are a few commands that might be useful to ensure consistent Python style:

```
make flake8  # Runs the Flake8 linter
make isort   # Sorts all imports
make tools   # Runs both Flake8 and isort
```

## Built With
This project utilizes Celery and Python

## Running Locally

If you would like to run this locally, you will need to specify the following environment variables:

1. `sysenv` (dev, ote, prod)
2. `DB_PASS` (Password for MongoDB)
3. `BROKER_PASS` (Password for Celery)
4. `WORKER_MODE` (needs to be `classify` or `scan`)
5. `ML_API_CERT` (path to `apiuser.cmap.int.` certificate)
6. `ML_API_KEY` (path to `apiuser.cmap.int.` key)
7. `API_JWT` (JWT for user who can create Abuse API tickets)

You may also need to configure settings.py and celeryconfig.py to specify additional MongoDB and Celery settings.

DCU Classifier can then be run locally by running `celery -A run worker -l INFO --without-gossip --without-heartbeat --without-mingle`