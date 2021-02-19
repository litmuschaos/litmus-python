### litmus-python:

This repo consists of Litmus Chaos Experiments written in Python. The examples in this repo are good indicators
of how to construct the various experiment pieces in python: complete with steady state checks, chaos injection,
chaosresult generation, post chaos checks, events generation, reports for observability etc..,

The chaos injection mechanism employed itself may vary ranging right from non-standard/custom approaches to reuse of
popular tools like chaostoolkit.

**NOTE**

- This repo can be viewed as an extension to the [litmuschaos/litmus](https://github.com/litmuschaos/litmus) repo
  in the sense that the litmus repo also houses a set of chaos experiments, built using ansible. The litmus repo
  will also continue to be the project's community-facing meta repo housing other important project arefacts.
  The litmus-python is very similar to and therefore a sister repo of [litmus-go](https://github.com/litmuschaos/litmus-go)
  which houses examples for experiment business logic written in golang.

### commit process
- Fork the project
    * checkout the project using 
    ```
    git clone git@github.com:sumitnagal/litmus-python.git
    ```
    * go to your folder 
    ```
    cd litmus-python
    ```
    * add upstream for main and intuit repo
    ```
    git remote add upstream git@github.com:litmuschaos/litmus-python.git
    git pull upstream master
    git checkout -b <branch name>
    ```
    * Make the changes and commit with signed
    ```
    git add .
    git commit -s -m "<message>"
    git push origin <branch>
    ```

### Appendix
- This repo moved from existing location of [test-tools/chaostoolkit](https://github.com/litmuschaos/test-tools/tree/master/chaostoolkit) to better serve as stand-alone project
