
import types
import time
from kubernetes.client.api import core_v1_api
from kubernetes.client.models.v1_event import V1Event
from kubernetes import client, config

import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
configuration = kubernetes.client.Configuration()
from datetime import datetime

#import "github.com/litmuschaos/litmus-go/pkg/types"
#import k8serrors "k8s.io/apimachinery/pkg/api/errors"
def deployment():
    #api_instance = client.CoreV1Api()
    with kubernetes.client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
        api_instance = kubernetes.client.AppsV1Api(api_client)
	#try:
    deployList = api_instance.list_namespaced_deployment(namespace="litmus")
    pprint("DeploymentList :", deployList)
	#except ApiException as e:
	#	return False, logger.Errorf("no deployment found with matching label, err: %v", e) 
	
    for deploy in range(deployList):
    	pprint(" List ", deploy)
    # if deploy.ObjectMeta.Annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue:
    # 		rsOwnerRef = targetPod.OwnerReferences
	# 	for own in range(rsOwnerRef) :
	# 		if own.Kind == "ReplicaSet" :
	# 			err = clients.KubeClient.AppsV1().ReplicaSets(chaosDetails.AppDetail.Namespace).Get(own.Name, v1.GetOptions{})
	# 			if err != None:
	# 				return False, err
				
	# 			ownerRef = rs.OwnerReferences
	# 			for _, own in range(ownerRef):
	# 				if own.Kind == "Deployment" & own.Name == deploy.Name:
	# 					log.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, deploy.Name, deploy.Namespace)
	# 					return True, None

deployment()
# #GetENV fetches all the env variables from the runner pod
# def GetENV(experimentDetails):
# 	experimentDetails.ExperimentName =  "pod-delete"
# 	experimentDetails.ChaosNamespace =  {
# 				'APIVersion': "litmuschaos.io/v1alpha1",
# 				'Kind':       "kind",
# 				'Name':       "eventsDetails.ResourceName",
# 				'Namespace':  "chaosDetails.ChaosNamespace",
# 				'UID':        "eventsDetails.ResourceUID",
# 			}
    

# class ExperimentDetails(object):
# 	def __init__(self, ExperimentName=None, ChaosNamespace=None):
# 		self.ExperimentName          = ExperimentName
# 		self.ChaosNamespace          = ChaosNamespace


# expe = ExperimentDetails(ChaosNamespace={
# 				'APIVersion': "litmuschaos.io/v1alpha1",
# 				'Kind':       "kind",
# 				'Name':       "eventsDetails.ResourceName",
# 				'Namespace':  "chaosDetails.ChaosNamespace",
# 				'UID':        "eventsDetails.ResourceUID",
# 			})
# print("Experiment Details : ", expe.ChaosNamespace)
# GetENV(expe)
# print("Experiment Details : ", expe.ChaosNamespace)
# #CreateEvents create the events in the desired resource
# api_instance = client.CoreV1Api()
# now = datetime.now()
# time_stamp = now.strftime("%H:%M:%S")

# body = client.V1Event(event_time=time_stamp, first_timestamp=time_stamp, 
# involved_object={
#     'APIVersion': "litmuschaos.io/v1alpha1",
#     'Kind':       "ChaosResult",
#     'Name':       "podtato-main-pod-delete-chaosjmltp-pod-delete",
#     'Namespace':  "litmus",
#     'UID':        "27a13709-6027-4003-9747-4eb5fa5d32c2",
# },  last_timestamp=time_stamp, message= "eventsDetails.Message", 
# metadata={
#     'Name':      "pod-delete-eem78v-cpmfr",
#     'Namespace': "litmus",
# }, reason="eventsDetails.Message", related=None, 
# reporting_component=None, reporting_instance=None, series=None, source={
#     'Component': "pod-delete-eem78v-cpmfr",
# }, type="normal", local_vars_configuration=None,
# count=1,
# )

# print("Body :", body.involved_object)
#api_response = api_instance.create_namespaced_event("litmus", body)
#pprint("check ----------------->",api_response)

# #CreateEvents create the events in the desired resource
# def CreateEvents(eventDetails, clients, chaosDetails, kind, eventName):
# 	apiv1 = client.CoreV1Api()
# 	body = kubernetes.client.V1Event()
# 	body = {
# openapi_types = {
#         'action': 'str',
#         'api_version': 'str',
#         'count': 'int',
#         'event_time': 'datetime',
#         'first_timestamp': 'datetime',
#         'involved_object': {
# 			'APIVersion': "litmuschaos.io/v1alpha1",
# 			'Kind':       kind,
# 			'Name':       eventsDetails.ResourceName,
# 			'Namespace':  chaosDetails.ChaosNamespace,
# 			'UID':        eventsDetails.ResourceUID,
# 		},
#         'kind': 'str',
#         'last_timestamp': 'datetime',
#         'message': eventsDetails.Message,
#         'metadata': {
# 			'Name':      eventName,
# 			'Namespace': chaosDetails.ChaosNamespace,
# 		},
#         'reason': eventsDetails.Message,
#         'related': 'V1ObjectReference',
#         'reporting_component': 'str',
#         'reporting_instance': 'str',
#         'series': 'V1EventSeries',
#         'source': {
# 			'Component': chaosDetails.ChaosPodName,
# 		},
#         'type': eventsDetails.Type,
#     }
# 	openapi_types = {
#         'action': 'str',
#         'api_version': 'str',
#         'count': 'int',
#         'event_time': 'datetime',
#         'first_timestamp': 'datetime',
#         'involved_object': {
# 			'APIVersion': "litmuschaos.io/v1alpha1",
# 			'Kind':       kind,
# 			'Name':       eventsDetails.ResourceName,
# 			'Namespace':  chaosDetails.ChaosNamespace,
# 			'UID':        eventsDetails.ResourceUID,
# 		},
#         'kind': 'str',
#         'last_timestamp': 'datetime',
#         'message': eventsDetails.Message,
#         'metadata': {
# 			'Name':      eventName,
# 			'Namespace': chaosDetails.ChaosNamespace,
# 		},
#         'reason': eventsDetails.Message,
#         'related': 'V1ObjectReference',
#         'reporting_component': 'str',
#         'reporting_instance': 'str',
#         'series': 'V1EventSeries',
#         'source': {
# 			'Component': chaosDetails.ChaosPodName,
# 		},
#         'type': eventsDetails.Type,
#     }
# 	}
# 	openapi_types = {
#         'action': 'str',
#         'api_version': 'str',
#         'count': 'int',
#         'event_time': 'datetime',
#         'first_timestamp': 'datetime',
#         'involved_object': {
# 			'APIVersion': "litmuschaos.io/v1alpha1",
# 			'Kind':       kind,
# 			'Name':       eventsDetails.ResourceName,
# 			'Namespace':  chaosDetails.ChaosNamespace,
# 			'UID':        eventsDetails.ResourceUID,
# 		},
#         'kind': 'str',
#         'last_timestamp': 'datetime',
#         'message': eventsDetails.Message,
#         'metadata': {
# 			'Name':      eventName,
# 			'Namespace': chaosDetails.ChaosNamespace,
# 		},
#         'reason': eventsDetails.Message,
#         'related': 'V1ObjectReference',
#         'reporting_component': 'str',
#         'reporting_instance': 'str',
#         'series': 'V1EventSeries',
#         'source': {
# 			'Component': chaosDetails.ChaosPodName,
# 		},
#         'type': eventsDetails.Type,
#     }
#     body = client.V1Event(openapi_types)

	#try:
    #    api_response = api_instance.create_namespaced_event(namespace, body, pretty=pretty, dry_run=dry_run, field_manager=field_manager)
    #    pprint(api_response)
    #except ApiException as e:
    #    print("Exception when calling CoreV1Api->create_namespaced_event: %s\n" % e)
	
	

#GenerateEvents update the events and increase the count by 1, if already present
# else it will create a new event
#def GenerateEvents(EventDetails, ClientSets, ChaosDetails, kind) 
	#eventName = eventsDetails.Reason + chaosDetails.ChaosPodName
	#err = CreateEvents(eventsDetails, clients, chaosDetails, kind, eventName); 
