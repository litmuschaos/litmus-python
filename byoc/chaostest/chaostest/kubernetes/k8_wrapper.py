import os
import argparse
import logging
import sys

from chaostest.utils.helper import Helper
from chaostest.utils.chasotoolkit_utils import ChaosUtils

__author__ = 'Sumit_Nagal@intuit.com'

logger = logging.getLogger(__name__)

####################################
# Start of Python Chaos Experiment #
####################################

parser = argparse.ArgumentParser()

parser.add_argument("-file", action='store',
                    default="pod-custom-kill-count.json",
                    dest="file",
                    help="Chaos file to chose for execution"
                    )
parser.add_argument("-exp", action='store',
                    default="k8-pod-delete",
                    dest="exp",
                    help="Chaos experiment to chose for execution"
                    )
parser.add_argument('-label', action='store',
                    dest='label',
                    default="app",
                    help='Store a label value')
parser.add_argument("-namespace", action='store',
                    default="default",
                    dest="namespace",
                    help="namespace for application"
                    )
parser.add_argument('-app', action='store',
                    dest='app',
                    default="localhost",
                    help='Store the application health endpoint hostname')
parser.add_argument('-app-healthcheck', action='store',
                    dest='app_healthcheck',
                    default="/health/full",
                    help='Store the application health endpoint URI')
parser.add_argument('-percentage', action='store',
                    dest='percentage',
                    default="50",
                    help='Store the application health endpoint')
parser.add_argument('-report', action='store',
                    dest='report',
                    default="false",
                    help='Option to upload the result to report server')
parser.add_argument('-report_endpoint', action='store',
                    dest='report_endpoint',
                    default="none",
                    help='Endpoint where the report data will be uploaded')
parser.add_argument("-testNamespace",
                    required=False,
                    default="none",
                    dest='testnamespace',
                    help="Kubernetes client ignore SSL")

results = parser.parse_args()

# adopt log structure used by the chaos-test framework
logging.basicConfig(
    format="[%(asctime)s %(levelname)-2s] [%(module)s:%(lineno)s] %(message)s",
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("chaostoolkit.log"),
        logging.StreamHandler(sys.stdout)
    ]
    )

env_params = dict(
    LABEL_NAME=results.label,
    NAME_SPACE=results.namespace,
    APP_ENDPOINT=results.app,
    APP_HEALTHCHECK=results.app_healthcheck,
    PERCENTAGE=int(results.percentage),
    FILE=results.file,
    REPORT=results.report,
    REPORT_ENDPOINT=results.report_endpoint,
    EXP=results.exp,
    TEST_NAMESPACE=results.testnamespace
)

# check (&set) env based on input and/or default values
for key in env_params:
    if key in os.environ.keys():
        logging.debug("Environment exists for key: %s", key)
        logging.debug("Environment exists for value: %s", os.environ[key])
        env_params[key] = os.environ[key]
    else:
        os.environ[key] = str(env_params[key])

filename = os.environ['FILE']
namespace = os.environ['NAME_SPACE']
experiment = os.environ['EXP']
report = os.environ['REPORT']
report_endpoint = os.environ['REPORT_ENDPOINT']
test_namespace = os.environ['TEST_NAMESPACE']

# if the env CHAOSENGINE is defined, suffix it standard experiment name
# to generate the fully-qualified chaos experiment/chaosresult name
engineName = os.environ['CHAOSENGINE']
if 'CHAOSENGINE' in os.environ.keys():
    experiment_name = os.environ['CHAOSENGINE']
else:
    experiment_name = experiment
    engineName = experiment

result_name = experiment
try:
    Helper().chaos_result_tracker(result_name, 'Running', 'Awaited', test_namespace, engineName)
    chaos_utils = ChaosUtils()
    test_result = chaos_utils.run_chaos_engine(filename, env_params, report, report_endpoint, engineName)
    Helper().chaos_result_tracker(result_name, 'Completed', Helper.TEST_RESULT_STATUS.get(test_result), test_namespace, engineName)
except Exception as ex:
    logger.error("Test Failed with exception " + str(ex))
    Helper().chaos_result_tracker(result_name, 'Completed', 'Failed', test_namespace, engineName)
