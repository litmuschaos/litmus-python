from kubernetes import client, config
import time
import logging
import logging
logger = logging.getLogger(__name__)
from chaosk8s import create_k8s_api_client
from jinja2 import Environment,  select_autoescape, PackageLoader
import os
import subprocess
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
import pkg.events.events as events
import pkg.types.types as types
from kubernetes import client, config, dynamic
from kubernetes.client import api_client
from kubernetes.client.api import core_v1_api
from distutils.util import strtobool

global conf
if os.getenv('KUBERNETES_SERVICE_HOST'):
    conf = config.load_incluster_config()
else:
    conf = config.load_kube_config()
core_v1 = client.CoreV1Api()

api_instance = client.AppsV1Api()
api = create_k8s_api_client(secrets = None)
env = os.environ

configuration = client.Configuration()

clientDyn = dynamic.DynamicClient(
    api_client.ApiClient(configuration=conf)
)
cli = api_client.ApiClient(configuration=configuration)
try:
    chaosResults = clientDyn.resources.get(api_version="litmuschaos.io/v1alpha1", kind="ChaosResult").get()
    resp = core_v1.list_namespaced_pod(namespace='litmus')
    if len(chaosResults.items) == 0:
        raise Exception
except:
	print("Done")
print(chaosResults.items[0].metadata.name)
print(resp.items[0].metadata.name)
	# try:
# 		deployList = api_instance.list_namespaced_deployment(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
# 	except ApiException as e:
# 	 	return False, logger.error("no deployment found with matching label, err: {}".format(e))