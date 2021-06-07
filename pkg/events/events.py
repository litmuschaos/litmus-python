
from kubernetes import client, config
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
from datetime import datetime

configuration = kubernetes.client.Configuration()


#CreateEvents create the events in the desired resource
def CreateEvents(eventsDetails, clients , chaosDetails, kind, eventName):
	api_instance = client.CoreV1Api(clients)
	now = datetime.now()
	time_stamp = now.strftime("%H:%M:%S")

	body = client.V1Event(event_time=time_stamp, first_timestamp=time_stamp, 
			involved_object={
				'APIVersion': "litmuschaos.io/v1alpha1",
				'Kind':       kind,
				'Name':       eventsDetails.ResourceName,
				'Namespace':  chaosDetails.ChaosNamespace,
				'UID':        eventsDetails.ResourceUID,
			},  last_timestamp=time_stamp, message= eventsDetails.Message, 
			metadata={
				'Name':      eventName,
				'Namespace': chaosDetails.ChaosNamespace,
			}, reason=eventsDetails.Message, related=None, 
			reporting_component=None, reporting_instance=None, series=None, source={
				'Component': chaosDetails.ChaosPodName,
			}, type=eventsDetails.Type, local_vars_configuration=None,
			count=1,
			)
	try:
		api_response = api_instance.create_namespaced_event(chaosDetails.ChaosNamespace, body)
		pprint(api_response)
	except ApiException as e:
		return e
	
	return None

#GenerateEvents update the events and increase the count by 1, if already present
# else it will create a new event
def GenerateEvents(eventsDetails, clients, chaosDetails, kind):
	now = datetime.now()
	time_stamp = now.strftime("%H:%M:%S")
	api_instance = client.CoreV1Api(clients)
	if kind == "ChaosResult":
		eventName = eventsDetails.Reason + chaosDetails.ChaosPodName
		err = CreateEvents(eventsDetails, clients, chaosDetails, kind, eventName)
		if err != None:
			return err
	elif kind == "ChaosEngine":
		eventName = eventsDetails.Reason + chaosDetails.ExperimentName + str(chaosDetails.ChaosUID)
		try:
			event = client.V1EventList(metadata= {
				'Name':      eventName,
				'Namespace': chaosDetails.ChaosNamespace,
			})
			pprint(event)
		except DagsterK8sError as e:
			err = CreateEvents(eventsDetails, clients, chaosDetails, kind, eventName)
			if err != None:
				return err
			return None
		event.LastTimestamp = time_stamp
		event.Count = event.Count + 1
		event.Source.Component = chaosDetails.ChaosPodName
		event.Message = eventsDetails.Message
		try:
			api_response = api_instance.patch_namespaced_event(eventName, chaosDetails.ChaosNamespace, event)
			pprint(api_response)
		except ApiException as e:
			return e
		return None
	return None
