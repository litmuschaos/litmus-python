#!/bin/bash

# Preserve order for chaos-test and lib in the beginning, thats the core
declare -a chaosexperiments=("chaostoolkit" "chaostoolkit-lib" "chaostoolkit-reporting" "chaostoolkit-kubernetes" "chaostoolkit-aws")
for chaosexperiment in "${chaosexperiments[@]}"
do
  pip install --no-cache-dir -U "$chaosexperiment"
done

# For json path and other custom packages you can use the below
declare -a packages=("jsonpath2")
for package in "${packages[@]}"
do
  pip install --no-cache-dir -U "$package"
  ls -ltr
done

# Chaos toolkit litmus local package installation
declare -a chaos_litmus_packages=("chaostest")
for chaos_litmus_package in "${chaos_litmus_packages[@]}"
do
  pwd
  cd "$chaos_litmus_package"
  ls -ltr
  python setup.py develop
  pip install -U .
done


rm -rf /tmp/* /root/.cache

#nohup kubectl proxy --port=8080 &>/dev/null &
#wait
