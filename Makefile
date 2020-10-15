# Makefile for building Containers for Storage Testing
# Reference Guide - https://www.gnu.org/software/make/manual/make.html

# Internal variables or constants.
# NOTE - These will be executed when any make target is invoked.
IS_DOCKER_INSTALLED       := $(shell which docker >> /dev/null 2>&1; echo $$?)

help:
	@echo ""
	@echo "Usage:-"
	@echo "\tmake deps              -- will verify build dependencies are installed"
	@echo "\tmake chaostest      -- will build and push python experiment images
	@echo ""

_build_check_docker:
	@if [ $(IS_DOCKER_INSTALLED) -eq 1 ]; \
		then echo "" \
		&& echo "ERROR:\tdocker is not installed. Please install it before build." \
		&& echo "" \
		&& exit 1; \
		fi;

deps: _build_check_docker
	@echo ""
	@echo "INFO:\tverifying dependencies for litmus-python ..."

_build_tests_chaostest_image:
	@echo "INFO: Building container image for performing chaostoolkit tests"
	cd chaos-test && docker build -t litmuschaos/chaostoolkit:ci .

_push_tests_chaostest_image:
	@echo "INFO: Publish container litmuschaos/chaostoolkit:ci"
	REPONAME="litmuschaos" IMGNAME="chaostoolkit" IMGTAG="ci" ./chaos-test/buildscripts/push

chaostest: deps _build_tests_chaostest_image _push_tests_chaostest_image
