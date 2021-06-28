
# Makefile for building Litmus and its tools
# Reference Guide - https://www.gnu.org/software/make/manual/make.html

#
# Internal variables or constants.
# NOTE - These will be executed when any make target is invoked.

IS_DOCKER_INSTALLED = $(shell which docker >> /dev/null 2>&1; echo $$?)

# Docker info
DOCKER_REPO ?= litmuschaos
DOCKER_IMAGE ?= py-runner
DOCKER_TAG ?= ci

.PHONY: help
help:
	@echo ""
	@echo "Usage:-"
	@echo "\tmake deps          	-- sets up dependencies for image build"
	@echo "\tmake build   			 -- docker multi-arch image"
	@echo "\tmake build-amd64   	-- builds the litmus-py docker amd64 image"
	@echo "\tmake push-amd64    	-- pushes the litmus-py amd64 image"
	@echo "\tmake build-amd64-byoc  -- builds the chaostest docker amd64 image"
	@echo "\tmake push-amd64-byoc   -- pushes the chaostest amd64 image"
	@echo ""

.PHONY: all
all: deps buildx build-byoc build-litmus-python trivy-check

.PHONY: deps
deps: _build_check_docker

_build_check_docker:
	@if [ $(IS_DOCKER_INSTALLED) -eq 1 ]; \
		then echo "" \
		&& echo "ERROR:\tdocker is not installed. Please install it before build." \
		&& echo "" \
		&& exit 1; \
		fi;

.PHONY: buildx
buildx: docker.buildx image-build

.PHONY: docker.buildx
docker.buildx:
	@echo "------------------------------"
	@echo "--> Setting up Builder        " 
	@echo "------------------------------"
	@if ! docker buildx ls | grep -q multibuilder; then\
		docker buildx create --name multibuilder;\
		docker buildx inspect multibuilder --bootstrap;\
		docker buildx use multibuilder;\
	fi

.PHONY: image-build
image-build:	
	@echo "-------------------------"
	@echo "--> Build builder image" 
	@echo "-------------------------"
	@docker buildx build --file Dockerfile --progress plane --platform linux/arm64,linux/amd64 --no-cache --tag $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG) .

.PHONY: build-litmus-python
build-litmus-python: build-py-runner push-py-runner

.PHONY: build-py-runner
build-py-runner:
	@echo "-------------------------"
	@echo "--> Build py-runner image" 
	@echo "-------------------------"
	@sudo docker build --file Dockerfile --tag $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG) . --build-arg TARGETARCH=amd64

.PHONY: push-py-runner
push-py-runner:
	@echo "-------------------"
	@echo "--> py-runner image" 
	@echo "-------------------"
	REPONAME="$(DOCKER_REPO)" IMGNAME="$(DOCKER_IMAGE)" IMGTAG="$(DOCKER_TAG)" ./build/push

.PHONY: build-byoc
build-byoc: build-chaostoolkit push-chaostoolkit

.PHONY: build-chaostoolkit
build-chaostoolkit:
	@echo "-------------------------"
	@echo "--> Build chaostoolkit image" 
	@echo "-------------------------"
	@sudo docker build --file byoc/Dockerfile --tag $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG) . --build-arg TARGETARCH=amd64

.PHONY: push-chaostoolkit
push-chaostoolkit:
	@echo "-------------------"
	@echo "--> chaostoolkit image" 
	@echo "-------------------"
	REPONAME="$(DOCKER_REPO)" IMGNAME="$(DOCKER_IMAGE)" IMGTAG="$(DOCKER_TAG)" ./build/push

.PHONY: trivy-check
trivy-check:

	@echo "------------------------"
	@echo "---> Running Trivy Check"
	@echo "------------------------"
	@./trivy --exit-code 0 --severity HIGH --no-progress $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	@./trivy --exit-code 0 --severity CRITICAL --no-progress $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG)
