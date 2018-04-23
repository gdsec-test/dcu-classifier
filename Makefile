REPONAME=infosec-dcu/dcu-classifier
BUILDROOT=$(HOME)/dockerbuild/$(REPONAME)
DOCKERREPO=artifactory.secureserver.net:10014/docker-dcu-local/dcu-classifier
DATE=$(shell date)
COMMIT=
BUILD_BRANCH=origin/master

# libraries we need to stage for pip to install inside Docker build
PRIVATE_PIPS=git@github.secureserver.net:ITSecurity/dcdatabase.git

.PHONY: prep dev prod ote clean prod-deploy ote-deploy dev-deploy

all: prep dev

prep:
	@echo "----- preparing $(REPONAME) build -----"
	# stage pips we will need to install in Docker build
	mkdir -p $(BUILDROOT)/private_pips && rm -rf $(BUILDROOT)/private_pips/*
	for entry in $(PRIVATE_PIPS) ; do \
		IFS=";" read repo revision <<< "$$entry" ; \
		cd $(BUILDROOT)/private_pips && git clone $$repo ; \
		if [ "$$revision" != "" ] ; then \
			name=$$(echo $$repo | awk -F/ '{print $$NF}' | sed -e 's/.git$$//') ; \
			cd $(BUILDROOT)/private_pips/$$name ; \
			current_revision=$$(git rev-parse HEAD) ; \
			echo $$repo HEAD is currently at revision: $$current_revision ; \
			echo Dependency specified in the Makefile for $$name is set to revision: $$revision ; \
			echo Reverting to revision: $$revision in $$repo ; \
			git reset --hard $$revision; \
		fi ; \
	done

	# copy the app code to the build root
	cp -rp ./* $(BUILDROOT)

prod: prep
	@echo "----- building $(REPONAME) prod -----"
	read -p "About to build production image from $(BUILD_BRANCH) branch. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	git fetch && git checkout $(BUILD_BRANCH)
	$(eval COMMIT:=$(shell git rev-parse --short HEAD))
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/' $(BUILDROOT)/k8s/prod/dcu-classifier.deployment.yml $(BUILDROOT)/k8s/prod/dcu-scanner.deployment.yml
	sed -ie 's/REPLACE_WITH_GIT_COMMIT/$(COMMIT)/' $(BUILDROOT)/k8s/prod/dcu-classifier.deployment.yml $(BUILDROOT)/k8s/prod/dcu-scanner.deployment.yml
	docker build -t $(DOCKERREPO):$(COMMIT) $(BUILDROOT)
	git checkout -

ote: prep
	@echo "----- building $(REPONAME) ote -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/ote/dcu-classifier.deployment.yml $(BUILDROOT)/k8s/ote/dcu-scanner.deployment.yml
	docker build -t $(DOCKERREPO):ote $(BUILDROOT)

dev: prep
	@echo "----- building $(REPONAME) dev -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/dev/dcu-classifier.deployment.yml $(BUILDROOT)/k8s/dev/dcu-scanner.deployment.yml
	docker build -t $(DOCKERREPO):dev $(BUILDROOT)

prod-deploy: prod
	@echo "----- deploying $(REPONAME) prod -----"
	docker push $(DOCKERREPO):$(COMMIT)
	kubectl --context prod apply -f $(BUILDROOT)/k8s/prod/dcu-classifier.deployment.yml --record
	kubectl --context prod apply -f $(BUILDROOT)/k8s/prod/dcu-scanner.deployment.yml --record

ote-deploy: ote
	@echo "----- deploying $(REPONAME) ote -----"
	docker push $(DOCKERREPO):ote
	kubectl --context ote apply -f $(BUILDROOT)/k8s/ote/dcu-classifier.deployment.yml --record
	kubectl --context ote apply -f $(BUILDROOT)/k8s/ote/dcu-scanner.deployment.yml --record

dev-deploy: dev
	@echo "----- deploying $(REPONAME) dev -----"
	docker push $(DOCKERREPO):dev
	kubectl --context dev apply -f $(BUILDROOT)/k8s/dev/dcu-classifier.deployment.yml --record
	kubectl --context dev apply -f $(BUILDROOT)/k8s/dev/dcu-scanner.deployment.yml --record

clean:
	@echo "----- cleaning $(REPONAME) app -----"
	rm -rf $(BUILDROOT)
