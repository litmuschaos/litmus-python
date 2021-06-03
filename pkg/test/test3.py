from kubernetes import client, config
import logging
logger = logging.getLogger(__name__)
# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
from chaoslib.types import Secrets

from chaosk8s import create_k8s_api_client

#field_selector = "metadata.name={name}".format(name=name)
api_instance = client.CoreV1Api()
api = create_k8s_api_client(secrets = None)
#api_instance = client.CoreV1Api(clients)
v1 = client.AppsV1beta1Api(api)
#if label_selector:
ret = v1.list_namespaced_deployment("litmus")
#else:
#ret = v1.list_namespaced_deployment(ns, field_selector=field_selector)
print("Found  ",ret)
#print("instance : ", api_response)
#print("service '{name}' is initialized".format(name=name))

# print("Active host is %s" % configuration.Configuration().host)

# with client.ApiClient(configuration) as api_client:
#     # Create an instance of the API class
#     api_instance = client.AppsV1Api(api_client)
# v1 = client.CoreV1Api()
# print("Listing pods with their IPs:")
# ret = client.V1DeploymentList() #list_namespaced_event("litmus") #list_pod_for_all_namespaces(watch=False)

# print(ret)
#for i in ret.items:
#    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))