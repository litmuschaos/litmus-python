from chaosk8s import create_k8s_api_client
from kubernetes.client import api_client
from kubernetes import client, config
import deserialize
from dagster_k8s.client import (
    DagsterK8sAPIRetryLimitExceeded,
    DagsterK8sError,
    DagsterK8sPipelineStatusException,
    DagsterK8sTimeoutError,
    DagsterK8sUnrecoverableAPIError,
)
config.load_kube_config()
api_instance = client.CoreV1Api()
pod = client.V1Pod
podLi = client.V1PodList

# try:
#     podl = api_instance.read #create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name="checks"))) #list_namespaced_pod("check") #list_namespaced_deployment("default")
# except DagsterK8sError as e:
#     print("Cannot create ns , err: {}".format(e.reason))
# # except Exception as e:
# #     print(e.reason)


events = client.V1Event
try:
    events  = api_instance.read_namespaced_event( name = str("Awaitedpod-delete"), namespace = "litmus") #list_namespaced_event(namespace = chaosDetails.ChaosNamespace)
			
    print(events)
except Exception as e:
    print("Error", e.reason)

events.count = 2

try:
    api_instance.patch_namespaced_event(name = str("Awaitedpod-delete"), namespace = "litmus", body=events)
except Exception as e:
    print(e)
#print(podl)
# print(len(podl.items))
# podLi.items = [podl.items[0]]
# v2 = client.ApiClient()
# #fake_kube_response = FakeKubeResponse(podList)
# #v1podList = v2.deserialize(fake_kube_response, 'V1Pod')
# for pod in podl.items:
    
#     print("1")
#     #podLi.items.append(pod)
#     #print("2")
# print((len(podLi.items)))
#print(podLi)
# 'api_version': 'apiVersion',
#         'kind': 'kind',
#         'metadata': 'metadata',
#         'spec': 'spec',
#         'status': 'status'