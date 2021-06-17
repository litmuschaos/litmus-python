# Chaos Toolkit for Litmus Chaos

## chaostest

The Chaos Toolkit aims to be the simplest and easiest way to explore building your own Chaos Engineering Experiments. It also aims to define a vendor and technology independent way of specifying Chaos Engineering experiments by providing an Open API.

Reference: https://chaostoolkit.org/

## Steps to install Chaos Toolkit

Install Python for your system:

1. On MacOS X:
   ```
   $ brew install python3
   ```

1. On Debian/Ubuntu:
   ```
   $ sudo apt-get install python3 python3-venv
   ```

1. On CentOS:
   ```
   $ sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
   $ sudo yum -y install python35u
   ```
   > **Note:**, on CentOS, the Python 3.5 binary is named python3.5 rather than python3 as other systems.

1. On Windows:
   ```
   Download the latest binary installer (https://www.python.org/downloads/windows/) from the Python website.
   ```
# Build Manually

   Dependencies can be installed for your system via its package management but, more likely, you will want to install them yourself in a local virtual environment.
1.
   ```
   $ python3 -m venv ~/.venvs/chaostk
   ```

1. Make sure to always activate your virtual environment before using it:

   ```
   $ source  ~/.venvs/chaostk/bin/activate
   ```

# Install chaostest CLI

1. Install chaostest in the virtual environment as follows:
   ```
   (chaostk) $ pip install chaostoolkit
   ```

1. You can verify the command was installed by running:
   ```
   (chaostk) $ chaos --version
   ```

# Local Development

1. In this directory
    ```
    cd litmus-python/byoc/chaostest
   ```
1. build python package
    ```
    python setup.py develop
   ```
1. In this directory
    ```
    cd litmus-python/byoc
    ```
1. build pip module
    ```
    pip install chaostest/
   ```


