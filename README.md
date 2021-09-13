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

`DCU Classifier` services (`classify` and/or `scan`) are made to run in parallel with `Auto Abuse ID`
*You need to be connected to the GoDaddy network (ie: VPN) because this reaches out to the ML API*

### Docker-compose, local docker images for dcu-classifier, dcu-scanner, auto_abuse_id and rabbitmq, with dev mongo

REDIS is needed for running auto_abuse_id locally in a docker container.

Environment variables for docker-compose:
1. `DB_PASS` (Password for dev MongoDB)
2. `API_TOKEN` for DCU Abuse (Scan API) shopper

Changes to docker-compose.yml file:
1. Replace `PATH_TO_YOUR_CERTS_DIRECTORY` with your local path to the `apiuser.cmap.int.dev-godaddy.com` crt and key files

* Run `docker-compose up -d` to run dcu-classifier, dcu-scanner, auto_abuse_id, rabbitmq and redis locally in a docker container.
* Run `docker logs -f dcu-classifier_auto-abuse-id_1` to view the run logs for auto_abuse_id
* Run `docker logs -f dcu-classifier_dcu-classifier_1` to view the run logs for dcu-classifier
* Run `docker logs -f dcu-classifier_rabbitmq_1` to view the run logs for rabbitmq
* Run `redis-cli` to interact with your local REDIS instance
* Browse to `127.0.0.1:15672` with creds `guest:guest` to view the management console for your local RabbitMQ

### Debug dcu-classifier locally, running against docker-compose auto_abuse_id, rabbitmq, redis and dev mongo

REDIS is needed for running auto_abuse_id locally in a docker container.

Environment variables for docker-compose:
1. `DB_PASS` (Password for dev MongoDB)

* Run `docker-compose up -d auto-abuse-id` to run auto_abuse_id, rabbitmq and redis locally in a docker container.
* Run `docker logs -f dcu-classifier_auto-abuse-id_1` to view the run logs for auto_abuse_id
* Run `docker logs -f dcu-classifier_rabbitmq_1` to view the run logs for rabbitmq
* Run `redis-cli` to interact with your local REDIS instance
* Browse to `127.0.0.1:15672` with creds `guest:guest` to view the management console for your local RabbitMQ

Environment variables for debugging dcu-classifier (ie: PyCharm)
1. `sysenv` Runtime env: `dev`
2. `DB_PASS` (Password for MongoDB)
3. `WORKER_MODE` (needs to be `classify` or `scan`, default is `classify`)
4. `ML_API_CERT` (path to `apiuser.cmap.int.` certificate)
5. `ML_API_KEY` (path to `apiuser.cmap.int.` key)
6. `API_TOKEN` for DCU Abuse (Scan API) shopper
7. `ABUSE_API_CREATE_URL` use `https://abuse.api.int.dev-godaddy.com/v1/abuse/tickets` for dev.
8. `LOG_LEVEL` (DEBUG or INFO, INFO is default)
9. `BROKER_URL` URL of RabbitMQ run via docker-compose: `amqp://guest@localhost:5672//`
10. `DISABLESSL` We dont need an ssl connection to local RabbitMQ: `False`

DCU Classifier can then be run/debugged locally by running `celery -A run worker -l debug -P solo`

### Debug dcu-classifier locally, running against env specific rabbitmq and mongo
If you would like to run this locally, you will need to specify the following environment variables:
1. `sysenv` (dev, ote, prod)
2. `DB_PASS` (Password for MongoDB)
3. `WORKER_MODE` (needs to be `classify` or `scan`, default is `classify`)
4. `ML_API_CERT` (path to `apiuser.cmap.int.` certificate)
5. `ML_API_KEY` (path to `apiuser.cmap.int.` key)
6. `API_TOKEN` for DCU Abuse (Scan API) shopper
7. `ABUSE_API_CREATE_URL` use `https://abuse.api.int.dev-godaddy.com/v1/abuse/tickets` for dev.
8. `LOG_LEVEL` (DEBUG or INFO, INFO is default)
9. `BROKER_PASS` RabbitMQ password for the `02d1081iywc7Av2` user
10. `SSO_USER` user to retrieve JWT with.
11. `SSO_PASSWORD` password to retrieve JWT with.

You may also need to configure settings.py and celeryconfig.py to specify additional MongoDB and Celery settings.

DCU Classifier can then be run/debugged locally by running `celery -A run worker -l debug -P solo`