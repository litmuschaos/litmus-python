# Makefile for building Containers for Storage Testing
# Reference Guide - https://www.gnu.org/software/make/manual/make.html

# Internal variables or constants.
# NOTE - These will be executed when any make target is invoked.
IS_DOCKER_INSTALLED       := $(shell which docker >> /dev/null 2>&1; echo $$?)

help:
	@echo ""
	@echo "Usage:-"
	@echo "\tmake deps              -- will verify build dependencies are installed"
	@echo "\tmake chaostoolkit      -- will build and push python experiment images 
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

_build_tests_chaostoolkit_image:
	@echo "INFO: Building container image for performing chaostoolkit tests"
	cd chaostoolkit && docker build -t litmuschaos/chaostoolkit .

_push_tests_chaostoolkit_image:
	@echo "INFO: Publish container litmuschaos/chaostoolkit"
	cd chaostoolkit/buildscripts && ./push

chaostoolkit: deps _build_tests_chaostoolkit_image _push_tests_chaostoolkit_image 

