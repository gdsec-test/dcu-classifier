REPONAME=digital-crimes/dcu-classifier
BUILDROOT=$(HOME)/dockerbuild/$(REPONAME)
DOCKERREPO=docker-dcu-local.artifactory.secureserver.net/dcu-classifier
DATE=$(shell date)
COMMIT=
BUILD_BRANCH=origin/main

define deploy_k8s
	docker push $(DOCKERREPO):$(2)
	cd k8s/$(1) && kustomize edit set image $$(docker inspect --format='{{index .RepoDigests 0}}' $(DOCKERREPO):$(2))
	kubectl --context $(1)-dcu apply -k k8s/$(1)
	cd k8s/$(1) && kustomize edit set image $(DOCKERREPO):$(1)
endef

define deploy_k3s
	docker push $(DOCKERREPO):$(2)
	cd k8s/$(1) && kustomize edit set image $$(docker inspect --format='{{index .RepoDigests 0}}' $(DOCKERREPO):$(2))
	kubectl --context $(1)-cset apply -k k8s/$(1)
	cd k8s/$(1) && kustomize edit set image $(DOCKERREPO):$(1)
endef

all: env

env:
	pip install -r test_requirements.txt
	pip install -r requirements.txt

.PHONY: flake8
flake8:
	@echo "----- Running linter -----"
	flake8 --config ./.flake8 .

.PHONY: isort
isort:
	@echo "----- Optimizing imports -----"
	isort --atomic .

.PHONY: tools
tools: flake8 isort

.PHONY: test
test:
	@echo "----- Running tests -----"
	sysenv=test python -m unittest discover -s ./tests -p *_tests.py

.PHONY: testcov
testcov:
	@echo "----- Running tests with coverage -----"
	sysenv=test nosetests tests --with-coverage --cover-erase --cover-package=service


.PHONY: prep
prep: tools test
	@echo "----- preparing $(REPONAME) build -----"
	mkdir -p $(BUILDROOT)
	cp -rp ./* $(BUILDROOT)
	cp -rp ~/.pip $(BUILDROOT)/pip_config

.PHONY: prod
prod: prep
	@echo "----- building $(REPONAME) $(build_version) -----"
	$(eval commit:=$(shell git rev-parse --short HEAD))
	docker build -t $(DOCKERREPO):$(commit) $(BUILDROOT)

.PHONY: ote
ote: prep
	@echo "----- building $(REPONAME) ote -----"
	docker build -t $(DOCKERREPO):ote $(BUILDROOT)

.PHONY: dev
dev: prep
	@echo "----- building $(REPONAME) $(build_version) -----"
	docker build -t $(DOCKERREPO):dev $(BUILDROOT)

.PHONY: test-env
test-env: prep
	@echo "----- building $(REPONAME) $(build_version) -----"
	docker build -t $(DOCKERREPO):test $(BUILDROOT)

.PHONY: prod-deploy
prod-deploy: prod
	$(eval commit:=$(shell git rev-parse --short HEAD))
	read -p "About to build production image from main branch. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	git fetch && git checkout $(build_branch)
	$(call deploy_k8s,prod,$(commit))

.PHONY: ote-deploy
ote-deploy: ote
	$(eval commit:=$(shell git rev-parse --short HEAD))
	read -p "About to build ote image from main branch. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	git fetch && git checkout $(build_branch)
	$(call deploy_k8s,ote,ote)

.PHONY: test-deploy
test-deploy: test-env
	@echo "----- deploying $(REPONAME) ote -----"
	$(call deploy_k3s,test,test)

.PHONY: dev-deploy
dev-deploy: dev
	@echo "----- deploying $(REPONAME) dev -----"
	$(call deploy_k3s,dev,dev)

.PHONY: clean
clean:
	@echo "----- cleaning $(REPONAME) app -----"
	rm -rf $(BUILDROOT)
