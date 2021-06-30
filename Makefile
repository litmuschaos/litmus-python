
# Makefile for building Litmus and its tools
# Reference Guide - https://www.gnu.org/software/make/manual/make.html

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
	@echo "\tmake deps				-- sets up dependencies for image build"
	@echo "\tmake build				-- builds the litmus-py multi-arch image"
	@echo "\tmake push				-- pushes the litmus-py multi-arch image"
	@echo "\tmake build-amd64			-- builds the litmus-py docker amd64 image"
	@echo "\tmake push-amd64			-- pushes the litmus-py amd64 image"
	@echo ""

.PHONY: all
all: deps build push

.PHONY: deps
deps: _build_check_docker

_build_check_docker:
	@if [ $(IS_DOCKER_INSTALLED) -eq 1 ]; \
		then echo "" \
		&& echo "ERROR:\tdocker is not installed. Please install it before build." \
		&& echo "" \
		&& exit 1; \
		fi;

.PHONY: build
build: docker.buildx image-build

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
	@echo "--> Build py-runner image" 
	@echo "-------------------------"
	@docker buildx build --file Dockerfile --progress plane --platform linux/arm64,linux/amd64 --no-cache --tag $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG) .

.PHONY: push
push: docker.buildx litmus-py-push

.PHONE: litmus-py-push
litmus-py-push:
	@echo "-------------------"
	@echo "--> py-runner image" 
	@echo "-------------------"
	REGISTRYNAME="$(DOCKER_REGISTRY)" REPONAME="$(DOCKER_REPO)" IMGNAME="$(DOCKER_IMAGE)" IMGTAG="$(DOCKER_TAG)" ./build/push

.PHONY: build-amd64 
build-amd64:
	@echo "-------------------------"
	@echo "--> Build py-runner amd64 image" 
	@echo "-------------------------"
	@sudo docker build --file Dockerfile --tag $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG) . --build-arg TARGETARCH=amd64

.PHONY: push-amd64
push-amd64:
	@echo "-------------------"
	@echo "--> push py-runner image" 
	@echo "-------------------"
	REPONAME="$(DOCKER_REPO)" IMGNAME="$(DOCKER_IMAGE)" IMGTAG="$(DOCKER_TAG)" ./build/push
