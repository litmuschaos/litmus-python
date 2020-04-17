# litmus-python: 

This repo consists of Litmus Chaos Experiments written in Python. The examples in this repo are good indicators 
of how to construct the experiments: complete with steady state checks, chaosresult generation, chaos injectionm, 
post chaos checks, create events and reports for observability and configure sinks for these. 

The chaos injection mechanism employed itself may vary ranging right from non-standard/custom approaches to reuse of
popular tools like chaostoolkit. 

**NOTE**

- This repo can be viewed as an extension to the [litmuschaos/litmus](https://github.com/litmuschaos/litmus) repo
  in the sense that the litmus repo also houses a significant set of experiments, built using ansible. The litmus repo 
  will also continue to be the project's community-facing meta repo housing other important project arefacts. In that 
  sense, litmus-python is very similar to and therefore a sister repo of [litmus-go](https://github.com/litmuschaos/litmus-go) which
  houses examples for experiment business logic written in golang. 


