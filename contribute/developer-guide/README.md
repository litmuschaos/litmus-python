## Steps to Bootstrap a Chaos Experiment

The artifacts associated with a chaos-experiment are summarized below: 

- Submitted in the litmuschaos/litmus-python repository, under the experiments/*chaos_category*/*experiment_name* folder 

  - Experiment business logic in python. May involve creating new or reusing an existing chaosLib 
  - Experiment test deployment manifest that is used for verification purposes
  - Experiment RBAC (holds experiment-specific ServiceAccount, Role and RoleBinding)

  Example: [pod delete experiment in litmus-python](/experiments/generic/pod_delete)

- Submitted in litmuschaos/chaos-charts repository, under the *chaos_category* folder

  - Experiment custom resource (CR) (holds experiment-specific chaos parameters & experiment entrypoint)
  - Experiment ChartServiceVersion (holds experiment metadata that will be rendered on [charthub](https://hub.litmuschaos.io/))
  - Experiment RBAC (holds experiment-specific ServiceAccount, Role and RoleBinding)
  - Experiment Engine (holds experiment-specific chaosengine)

  Example: [pod delete experiment in chaos-charts](https://github.com/litmuschaos/chaos-charts/tree/master/charts/generic/pod-delete)

The *generate_experiment.py* script is a simple way to bootstrap your experiment, and helps create the aforementioned artifacts in the 
appropriate directory (i.e., as per the chaos_category) based on an attributes file provided as input by the chart-developer. The 
scaffolded files consist of placeholders which can then be filled as desired.  

### Pre-Requisites

- *python3* is available (`sudo apt-get install python3`) 
- *jinja2* & *pyYaml* python packages are available (`sudo apt-get install python3-pip`, `pip install jinja2`, `pip install pyYaml`) 

### Steps to Generate Experiment Manifests

- Clone the litmus-python repository & navigate to the `contribute/developer-guide` folder

  ```
  $ git clone https://github.com/litmuschaos/litmus-python.git
  $ cd litmus-python/contribute/developer-guide
  ```

- Populate the `attributes.yaml` with details of the chaos experiment (or chart). Use the [attributes.yaml.sample](/contribute/developer-guide/attributes.yaml.sample) as reference. 

  As an example, let us consider an experiment to kill one of the replicas of a nginx deployment. The attributes.yaml can be constructed like this: 
  
  ```yaml
  $ cat attributes.yaml 
  
  ---
  name: "sample_exec_chaos"
  version: "0.1.0"
  category: "sample_category"
  repository: "https://github.com/litmuschaos/litmus-python/tree/master/sample_category/sample_exec_chaos"
  community: "https://kubernetes.slack.com/messages/CNXNB0ZTN"
  description: "it execs inside target pods to run the chaos inject commands, waits for the chaos duration and reverts the chaos"
  keywords:
    - "pods"
    - "kubernetes"
    - "sample-category"
    - "exec"
  platforms:
    - Minikube
  scope: "Namespaced"
  auxiliaryappcheck: false
  permissions:
    - apigroups:
        - ""
        - "batch"
        - "apps"
        - "litmuschaos.io"
      resources:
        - "jobs"
        - "pods"
        - "pods/log"
        - "events"
        - "deployments"
        - "replicasets"
        - "pods/exec"
        - "chaosengines"
        - "chaosexperiments"
        - "chaosresults"
      verbs:
        - "create"
        - "list"
        - "get"
        - "patch"
        - "update"
        - "delete"
        - "deletecollection"
  maturity: "alpha"
  maintainers:
    - name: "oumkale"
      email: "oumkale@chaosnative.com" 
  provider:
    name: "ChaosNative"
  minkubernetesversion: "1.12.0"
  references:
    - name: Documentation
      url: "https://docs.litmuschaos.io/docs/getstarted/"

  ```

- Run the following command to generate the necessary artefacts for submitting the `sample_category` chaos chart with 
  `sample_exec_chaos` experiment.

  ```
  $ python3 generate_experiment.py -f=attributes.yaml -g=<generate-type>
  ```

  **Note**: Replace the `-g=<generate-type>` placeholder with the appropriate value based on the usecase: 
  - `experiment`: Chaos experiment artifacts belonging to an existing OR new experiment.
  - `chart`: Just the chaos-chart metadata, i.e., chartserviceversion.yaml
      - Provide the type of chart in the `-t=<type>` flag. It supports the following values:
           - `category`: It creates the chart metadata for the category i.e chartserviceversion, package manifests
           - `experiment`: It creates the chart for the experiment i.e chartserviceversion, engine, rbac, experiment manifests
           - `all`: it creates both category and experiment charts (default type)

  - Provide the path of the attribute.yaml manifest in the `-f` flag.

  View the generated files in `/experiments/<chaos_category>` folder.

  ```
  $ cd /experiments

  $ ls -ltr

  total 8
  -rw-rw-r-- 1 oumkale oumkale    0 Jul  7 16:44 __init__.py
  drwxrwxr-x 3 oumkale oumkale 4096 Jul  7 16:44 generic/
  drwxrwxr-x 3 oumkale oumkale 4096 Jul  7 16:47 sample_category/

  $ ls -ltr sample_category/

  total 4
  -rw-rw-r-- 1 oumkale oumkale    0 Jul  7 16:50 __init__.py
  drwxr-xr-x 5 oumkale oumkale 4096 July 7 16:51 sample_exec_chaos/
  
  $ ls -ltr sample_category/sample_exec_chaos/

  total 12
  -rw-rw-r-- 1 oumkale oumkale    0 Jul  7 16:47 __init__.py
  drwxrwxr-x 2 oumkale oumkale 4096 Jul  7 16:48 experiment/
  drwxrwxr-x 2 oumkale oumkale 4096 Jul  7 16:49 charts/ 
  drwxrwxr-x 2 oumkale oumkale 4096 Jul  7 16:50 test/ 

  $ ls -ltr sample_category/sample_exec_chaos/experiment

  total 8
  -rw-rw-r-- 1 oumkale oumkale    0 Jul  7 18:43 __init__.py
  -rw-rw-r-- 1 oumkale oumkale 6440 Jul  7 18:47 sample_exec_chaos.py

  $ ls -ltr sample_category/charts

  total 24
  -rw-rw-r-- 1 oumkale oumkale  144 Jul  7 18:48 sample_category.package.yaml
  -rw-rw-r-- 1 oumkale oumkale  848 Jul  7 18:48 sample_category.category_chartserviceversion.yaml
  -rw-rw-r-- 1 oumkale oumkale  989 Jul  7 18:48 sample_exec_chaos.experiment_chartserviceversion.yaml
  -rw-rw-r-- 1 oumkale oumkale 1540 Jul  7 18:48 experiment.yaml
  -rw-rw-r-- 1 oumkale oumkale 1224 Jul  7 18:48 rbac.yaml
  -rw-rw-r-- 1 oumkale oumkale  731 Jul  7 18:48 engine.yaml

  $ ls -ltr sample-category/sample-exec-chaos/test

  total 4
  -rw-r--r-- 1 oumkale oumkale  1039 July 7 18:52 test.yaml
  
  $ ls -ltr chaosLib
  total 4
  -rw-rw-r-- 1 oumkale oumkale    0 Jul  7 16:44 __init__.py
  drwxrwxr-x 4 oumkale oumkale 4096 Jul  7 18:43 litmus

  $ ls -ltr chaosLib/litmus
  total 8
  drwxrwxr-x 3 oumkale oumkale 4096 Jul  7 16:44 pod_delete
  -rw-rw-r-- 1 oumkale oumkale    0 Jul  7 16:44 __init__.py
  drwxrwxr-x 2 oumkale oumkale 4096 Jul  7 18:43 sample_exec_chaos

  $ ls -ltr chaosLib/litmus/sample_exec_chaos
  total 8
  -rw-rw-r-- 1 oumkale oumkale    0 Jul  7 18:43 __init__.py
  -rw-rw-r-- 1 oumkale oumkale 5828 Jul  7 18:47 sample_exec_chaos.py
  
  ```
 
- Proceed with construction of business logic inside the `sample_exec_chaos.py` file, by making
  the appropriate modifications listed below to achieve the desired effect: 

  - variables 
  - entry & exit criteria checks for the experiment 
  - helper utils in either [pkg](/pkg/) or new [base chaos libraries](/chaosLib) 

- The chaosLib is created at `chaosLib/litmus/sample_exec_chaos/lib/sample_exec_chaos.py` path. It contains some pre-defined steps which runs the `ChaosInject` command (explicitly provided as an ENV var in the experiment CR). Which will induce chaos in the target application. It will wait for the given chaos duration and finally runs the `ChaosKill` command (also provided as an ENV var) for cleanup purposes. Update this chaosLib to achieve the desired effect based on the use-case or reuse the other existing chaosLib.

- Create an experiment README explaining, briefly, the *what*, *why* & *how* of the experiment to aid users of this experiment. 

### Steps to Test Experiment 

We can use [Okteto](https://github.com/okteto/okteto) to help us in performing the dev-tests for experiment created. 
Follow the steps provided below to setup okteto & test the experiment execution. 

- Install the Okteto CLI 

  ```
  curl https://get.okteto.com -sSfL | sh
  ```

- (Optional) Create a sample nginx deployment that can be used as the application under test (AUT).

  ```
  kubectl create deployment nginx --image=nginx
  ```

- Setup the RBAC necessary for execution of this experiment by applying the generated `rbac.yaml`

  ```
  kubectl apply -f rbac.yaml
  ```

- Modify the `test/test.yaml` with the desired values (app & chaos info) in the ENV and appropriate `chaosServiceAccount` along 
  with any other dependencies, if applicable (configmaps, volumes etc.,) & create this deployment  

  ```
  kubectl apply -f test/test.yml
  ```

- Go to the root of this repository (litmuschaos/litmus-python) & launch the Okteto development environment in your workspace.
  This should take you to the bash prompt on the dev container into which the content of the litmus-python repo is loaded. 
  
  - Note : 
    -  Replace `_` in chart manifest with `-` ex: sample_category to sample-category. Don't replace in directory name.
    -  Add packages routes for all the files which are generated from sdk in `setup.py` before creating image. 
      example :
      ```
      'chaosLib/litmus/sample_exec_chaos',
      'chaosLib/litmus/sample_exec_chaos/lib',
      'pkg/sample_category',
      'pkg/sample_category/environment',
      'pkg/sample_category/types',
      'experiments/sample_category',
      'experiments/sample_category/sample_exec_chaos',
      'experiments/sample_category/sample_exec_chaos/experiment',
      ```
    - Add `&` operator at the end of chaos commands `CHAOS_INJECT_COMMAND` example: `md5sum /dev/zero &`. 
      As we are running chaos commands as a background process in a separate thread.  
    - Import main file it in bin/experiment/experiment.py and add case. example: line number 3 in experiment.py 
    - Then go to root(litmus-python) and run `python3 setup.py install`

  ```
  root@test:~/okteto/litmus-python# okteto up 

  Deployment litmus-python doesn't exist in namespace litmus. Do you want to create a new one? [y/n]: y
  ✓  Development container activated
  ✓  Files synchronized

  The value of /proc/sys/fs/inotify/max_user_watches in your cluster nodes is too low.
  This can affect file synchronization performance.
  Visit https://okteto.com/docs/reference/known-issues/index.html for more information.
      Namespace: default
      Name:      litmus-experiment
      Forward:   2345 -> 2345
                 8080 -> 8080

  Welcome to your development container. Happy coding!
  ```

  This dev container inherits the env, serviceaccount & other properties specified on the test deployment & is now suitable for 
  running the experiment.

- Execute the experiment against the sample app chosen & verify the steps via logs printed on the console.

  ```
  python3 bin/experiment/experiment.py -name=<experiment-name>
  ``` 

- In parallel, observe the experiment execution via the changes to the pod/node state

  ```
  watch -n 1 kubectl get pods,nodes
  ```

- If there are necessary changes to the code based on the run, make them via your favourite IDE. 
  These changes are automatically reflected on the dev container. Re-run the experiment to confirm changes. 

- Once the experiment code is validated, stop/remove the development environment 

  ```
  root@test:~/okteto/litmus-python# okteto down
  ✓  Development container deactivated
  i  Run 'okteto push' to deploy your code changes to the cluster
  ```

- (Optional) Once the experiment has been validated using the above step, it can also be tested against the standard Litmus chaos 
  flow. This involves: 
  The experiment created using the above steps, can be tested in the following manner: 

- Run the `experiment.yml` with the desired values in the ENV and appropriate `chaosServiceAccount` 
  using a custom dev image instead of `litmuschaos/litmus-python` (say, oumkale/litmus-python) that packages the 
  business logic.
  - Creating a custom image built with the code validated by the previous steps
  - Launching the Chaos-Operator
  - Modifying the ChaosExperiment manifest (experiment.yaml) with right defaults (env & other attributes, as applicable) & creating 
    this CR on the cluster (pointing the `.spec.definition.image` to the custom one just built)
  - Modifying the ChaosEngine manifest (engine.yaml) with right app details, run properties & creating this CR to launch the chaos pods
  - Verifying the experiment status via ChaosResult 

  Refer [litmus docs](https://docs.litmuschaos.io/docs/getstarted/) for more details on performing each step in this procedure.

### Steps to Include the Chaos Charts/Experiments into the ChartHub

- Send a PR to the [litmus-python](https://github.com/litmuschaos/litmus-python) repo with the modified experiment files, rbac, 
  test deployment & README.
- Send a PR to the [chaos-charts](https://github.com/litmuschaos/chaos-charts) repo with the modified experiment CR, 
  experiment chartserviceversion, rbac, (category-level) chaos chart chartserviceversion & package.yaml (if applicable). 
