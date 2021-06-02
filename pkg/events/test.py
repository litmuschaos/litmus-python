
import types
import time
from kubernetes.client.api import core_v1_api
from kubernetes.client.models.v1_event import V1Event
from kubernetes import client, config

from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
configuration = kubernetes.client.Configuration()

#import "github.com/litmuschaos/litmus-go/pkg/types"
#import k8serrors "k8s.io/apimachinery/pkg/api/errors"


#CreateEvents create the events in the desired resource
def CreateEvents(eventDetails, clients, chaosDetails, kind, eventName):
	apiv1 = client.CoreV1Api()
	body = kubernetes.client.V1Event()
	body = {
openapi_types = {
        'action': 'str',
        'api_version': 'str',
        'count': 'int',
        'event_time': 'datetime',
        'first_timestamp': 'datetime',
        'involved_object': {
			'APIVersion': "litmuschaos.io/v1alpha1",
			'Kind':       kind,
			'Name':       eventsDetails.ResourceName,
			'Namespace':  chaosDetails.ChaosNamespace,
			'UID':        eventsDetails.ResourceUID,
		},
        'kind': 'str',
        'last_timestamp': 'datetime',
        'message': eventsDetails.Message,
        'metadata': {
			'Name':      eventName,
			'Namespace': chaosDetails.ChaosNamespace,
		},
        'reason': eventsDetails.Message,
        'related': 'V1ObjectReference',
        'reporting_component': 'str',
        'reporting_instance': 'str',
        'series': 'V1EventSeries',
        'source': {
			'Component': chaosDetails.ChaosPodName,
		},
        'type': eventsDetails.Type,
    }
	openapi_types = {
        'action': 'str',
        'api_version': 'str',
        'count': 'int',
        'event_time': 'datetime',
        'first_timestamp': 'datetime',
        'involved_object': {
			'APIVersion': "litmuschaos.io/v1alpha1",
			'Kind':       kind,
			'Name':       eventsDetails.ResourceName,
			'Namespace':  chaosDetails.ChaosNamespace,
			'UID':        eventsDetails.ResourceUID,
		},
        'kind': 'str',
        'last_timestamp': 'datetime',
        'message': eventsDetails.Message,
        'metadata': {
			'Name':      eventName,
			'Namespace': chaosDetails.ChaosNamespace,
		},
        'reason': eventsDetails.Message,
        'related': 'V1ObjectReference',
        'reporting_component': 'str',
        'reporting_instance': 'str',
        'series': 'V1EventSeries',
        'source': {
			'Component': chaosDetails.ChaosPodName,
		},
        'type': eventsDetails.Type,
    }
	}
	openapi_types = {
        'action': 'str',
        'api_version': 'str',
        'count': 'int',
        'event_time': 'datetime',
        'first_timestamp': 'datetime',
        'involved_object': {
			'APIVersion': "litmuschaos.io/v1alpha1",
			'Kind':       kind,
			'Name':       eventsDetails.ResourceName,
			'Namespace':  chaosDetails.ChaosNamespace,
			'UID':        eventsDetails.ResourceUID,
		},
        'kind': 'str',
        'last_timestamp': 'datetime',
        'message': eventsDetails.Message,
        'metadata': {
			'Name':      eventName,
			'Namespace': chaosDetails.ChaosNamespace,
		},
        'reason': eventsDetails.Message,
        'related': 'V1ObjectReference',
        'reporting_component': 'str',
        'reporting_instance': 'str',
        'series': 'V1EventSeries',
        'source': {
			'Component': chaosDetails.ChaosPodName,
		},
        'type': eventsDetails.Type,
    }
    body = client.V1Event(openapi_types)

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
