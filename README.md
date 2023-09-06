# litmus-python:

[![Slack Channel](https://img.shields.io/badge/Slack-Join-purple)](https://slack.litmuschaos.io)
![GitHub Workflow](https://github.com/litmuschaos/litmus-python/actions/workflows/push.yml/badge.svg?branch=master)
[![Docker Pulls](https://img.shields.io/docker/pulls/litmuschaos/py-runner.svg)](https://hub.docker.com/r/litmuschaos/py-runner)
[![GitHub issues](https://img.shields.io/github/issues/litmuschaos/litmus-python)](https://github.com/litmuschaos/litmus-python/issues)
[![Twitter Follow](https://img.shields.io/twitter/follow/litmuschaos?style=social)](https://twitter.com/LitmusChaos)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/5298/badge)](https://bestpractices.coreinfrastructure.org/projects/5298)
[![YouTube Channel](https://img.shields.io/badge/YouTube-Subscribe-red)](https://www.youtube.com/channel/UCa57PMqmz_j0wnteRa9nCaw)
<br>

- This repo consists of Litmus Chaos Experiments written in python. The examples in this repo are good indicators of how to construct the experiments in python: complete with steady state checks, chaosresult generation, chaos injection,
post chaos checks, create events and reports for observability and configure sinks for these.

**NOTE**

- This repo can be viewed as an extension to the [litmuschaos/litmus](https://github.com/litmuschaos/litmus) repo. The litmus repo will also continue to be the project's community-facing meta repo housing other important project artifacts. In that sense, litmus-py is very similar to and therefore a sister repo of [litmus-go](https://github.com/litmuschaos/litmus-go) which houses examples for experiment business logic written in go.

## Litmus SDK

The Litmus SDK provides a simple way to bootstrap your experiment and helps create the aforementioned artifacts in the appropriate directory (i.e., as per the chaos-category) based on an attributes file provided as input by the chart-developer. The scaffolded files consist of placeholders which can then be filled as desired.

It generates the custom chaos experiments with some default Pre & Post Chaos Checks (AUT & Auxiliary Applications status checks). It can use the existing chaoslib (present inside /chaoslib directory), if available else It will create a new chaoslib inside the corresponding directory.

Refer [Litmus-SDK](https://github.com/litmuschaos/litmus-python/blob/master/contribute/developer-guide/README.md) for more details

### Overview

Litmus-Python chaos experiments are fundamental units within the LitmusChaos architecture. Users can choose between readily available chaos experiments or create new ones to construct a required Chaos Workflow.

To know more about LitmusChaos experiments [refer](https://litmuschaos.github.io/litmus/) to this.

#### Experiment Flow :
 - Experiment business logic image has to be updated in `spec.definition.image` along with experiment entrypoint and tunable parameters in ChaosEngine (CR) which holds experiment-specific chaos parameters. ChaosExperiment is created by chaos runner which is managed by chaos operator [Refer litmus-python pod-delete experiment](https://github.com/litmuschaos/chaos-charts/blob/master/charts/generic/pod-delete/python/experiment.yaml)
  - Chaos Engine holds experiment-specific parameters. This CR is also updated/patched with the status of the chaos experiments, making it the single source of truth concerning the chaos.
  - Now we need to fit Experiment and Engine into the workflow, Chaos Workflow is a set of different operations coupled together to achieve desired chaos impact on a Kubernetes Cluster. LitmusChaos leverages the popular workflow & GitOps tool, Argo, to achieve this. 
    - Add experiment manifest in `install-experiment` artifacts and engine in `run-chaos` artifacts. 
    - Follow the steps in [pod-delete workflow](https://github.com/litmuschaos/chaos-charts/blob/master/workflows/pod-delete/workflow.yaml) or [User guide](https://docs.litmuschaos.io/docs/user-guides/construct-workflow/)
  - Now fork and clone [chaos-charts](https://github.com/litmuschaos/chaos-charts), Enter into [workflow](https://github.com/litmuschaos/chaos-charts/tree/master/workflows) directory.
    - Enter into `charts` directory to add charts which has been generated using sdk, for [reference](https://github.com/litmuschaos/chaos-charts/tree/master/charts/cassandra)
    - Enter into `workflow` directory and add workflow manifests for [reference](https://github.com/litmuschaos/chaos-charts/tree/master/workflows/podtato-head)
    - Connect your Git repository with chaos-center [ChaosHub](https://docs.litmuschaos.io/docs/concepts/chaoshub/)
  - Workflow can be added as a predefined workflow in Github and users can test by following the given steps:
    - Fork and clone [chaos-charts](https://github.com/litmuschaos/chaos-charts), now Enter into [workflow](https://github.com/litmuschaos/chaos-charts/tree/master/workflows) directory.
    - Follow the same structure for your workflow and push it. For [example](https://github.com/litmuschaos/chaos-charts/tree/master/workflows/podtato-head)
    - Connect your Git repository with chaos-center [ChaosHub](https://docs.litmuschaos.io/docs/concepts/chaoshub/)
  - Schedule your workflow with chaos-center in [given](https://docs.litmuschaos.io/docs/user-guides/schedule-workflow) manner, by selecting your connected [ChaosHub](https://docs.litmuschaos.io/docs/user-guides/schedule-workflow/#2-choose-a-workflow)
    - To Run your [first workflow](https://docs.litmuschaos.io/docs/getting-started/run-your-first-workflow/) follow the step-by-step guidelines.
    - After scheduling it one can [observe the workflow](https://docs.litmuschaos.io/docs/user-guides/observe-workflow)
    - To [Analyze the workflow](https://docs.litmuschaos.io/docs/user-guides/analyze-workflow/#)  follow these guidelines
    - Now User can [setup own Observablity](https://docs.litmuschaos.io/docs/user-guides/observability-set-up) and [Compare](https://docs.litmuschaos.io/docs/user-guides/comparative-analysis) it with other scheduled workflows with the help of monitoring dashboard
  - It can be scheduled for repeated execution.
    -  Select [edit Schedule](https://docs.litmuschaos.io/docs/user-guides/edit-schedule#3-change-the-schedule) to schedule recurrent workflow by selecting proper timing.
    - [Refer manifest](https://github.com/litmuschaos/chaos-charts/blob/master/workflows/podtato-head/workflow_cron.yaml) manifest.

## How to get started?

Refer the LitmusChaos documentation [litmus docs](https://docs.litmuschaos.io)

## How do I contribute?

You can contribute by raising issues, improving the documentation, contributing to the core framework and tooling, etc.

Head over to the [Contribution guide](CONTRIBUTING.md)

### Blogs
- [Create Chaos Experiments Using the LitmusChaos Python SDK](https://dev.to/oumkale/create-chaos-experiments-using-the-litmuschaos-python-sdk-4492)

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Flitmuschaos%2Flitmus-python.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Flitmuschaos%2Flitmus-python?ref=badge_large)
