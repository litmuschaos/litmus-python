from chaosk8s import create_k8s_api_client
from kubernetes.client import api_client
from kubernetes import client, config
import deserialize

config.load_kube_config()
api_instance = client.CoreV1Api()
podList = client.V1Pod
podLi = client.V1PodList
class FakeKubeResponse:
    def __init__(self, obj):
        import json
        self.data = json.dumps(obj)


try:
    deployList = api_instance.list_namespaced_pod("default") #list_namespaced_deployment("default")
except Exception as e:
    print("no deployment found with matching label, err: {}".format(e))
podList(api_version= deployList.items[0].api_version,
        kind = deployList.items[0].kind,
        metadata= deployList.items[0].metadata,
        spec = deployList.items[0].spec,
        status = deployList.items[0].status
        )
podLi.items = [podList]
v2 = client.ApiClient()
fake_kube_response = FakeKubeResponse(podList)
v1podList = v2.deserialize(fake_kube_response, 'V1Pod')
print(v1podList)
#print(podLi)
# 'api_version': 'apiVersion',
#         'kind': 'kind',
#         'metadata': 'metadata',
#         'spec': 'spec',
#         'status': 'status'