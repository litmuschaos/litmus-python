from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
api_instance = client.CoreV1Api()
body2 = {
'action': 'str',
'api_version': 'v1',
'count': 'int',
'event_time': 'datetime',
'first_timestamp': 'datetime',
'involved_object': {
    'APIVersion': "litmuschaos.io/v1alpha1",
    'Kind':       "chaosengine",
    'Name':       "Oum",
    'Namespace':  "litmus",
    'UID':        "oumkale",
},
'kind': 'str',
'last_timestamp': 'datetime',
'message': "jai ho",
'metadata': {
    'Name':      "eventName",
    'Namespace': "litmus",
},
'reason': "eventsDetails.Message",
'related': 'V1ObjectReference',
'reporting_component': 'str',
'reporting_instance': 'str',
'series': 'V1EventSeries',
'source': {
    'Component': "Oum",
},
'type': "eventsDetails.Type",
}

#print("Body : ", body2)
body = client.V1Event(kind= "ChaosEngine",api_version='app/v1',event_time=None, first_timestamp=None, 
			involved_object={
    'APIVersion': "litmuschaos.io/v1alpha1",
    'Kind':       "chaosengine",
    'Name':       "Oum",
    'Namespace':  "litmus",
    'UID':        "oumkale",
},  last_timestamp=None, message= "eventsDetails.Message", 
			metadata={
    'Name':      'eventName',
    'Namespace': 'litmus',
},)
pretty = 'pretty_example'
try:
    print("Body :", body)
    api_response = api_instance.create_namespaced_event('litmus', body)
    print("Dekho yaha" ,api_response)
except ApiException as e:
    print("Exception when calling CoreV1Api->create_namespaced_event: %s\n" % e)

#v1 = client.CoreV1Api()
#print("Listing pods with their IPs:")
#ret = v1.list_pod_for_all_namespaces(watch=False)
#for i in ret.items:
#    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))