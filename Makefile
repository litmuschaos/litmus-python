# Makefile for building Litmus and its tools
# Reference Guide - https://www.gnu.org/software/make/manual/make.html

#
# Internal variables or constants.
# NOTE - These will be executed when any make target is invoked.
#
IS_DOCKER_INSTALLED = $(shell which docker >> /dev/null 2>&1; echo $$?)

# Docker info
DOCKER_REPO ?= litmuschaos
DOCKER_IMAGE ?= python-runner
DOCKER_TAG ?= ci

.PHONY: help
help:
	@echo ""
	@echo "Usage:-"
	@echo "\tmake litmuspython  --  will build and push the litmus-python image"
	@echo "\tmake chaostest     -- will build and push python experiment images
	@echo ""


deps: _build_check_docker
	@echo ""
	@echo "INFO:\tverifying dependencies for litmus-python ..."

_build_tests_litmus_python_image:
	@echo "INFO: Building container image for performing chaostoolkit tests"
	docker build -t litmuschaos/litmus-python:ci .

_push_tests_litmus_python_image:
	@echo "INFO: Publish container litmuschaos/litmus-python:ci"
	cd ./build/push


litmuspython: deps _build_tests_litmus_python_image _push_tests_litmus_python_image


_build_tests_chaostest_image:
	@echo "INFO: Building container image for performing chaostoolkit tests"
	cd byoc && docker build -t litmuschaos/chaostoolkit:ci .

_push_tests_chaostest_image:
	@echo "INFO: Publish container litmuschaos/chaostoolkit:ci"
	REPONAME="litmuschaos" IMGNAME="chaostoolkit" IMGTAG="ci" ./byoc/buildscripts/push

chaostest: deps _build_tests_chaostest_image _push_tests_chaostest_image

