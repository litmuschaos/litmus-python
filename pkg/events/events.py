from datetime import datetime
import pytz
from kubernetes import client
import pkg.utils.k8serror.k8serror as k8serror

#CreateEvents create the events in the desired resource
def CreateEvents(eventsDetails , chaosDetails, kind, eventName, clients):
	
	event = client.V1Event(
			first_timestamp 	= datetime.now(pytz.utc),
			last_timestamp 		=  datetime.now(pytz.utc),
			event_time 		= datetime.now(pytz.utc),
			involved_object	= client.V1ObjectReference(
				api_version	= "litmuschaos.io/v1alpha1",
				kind     	= kind,
				name     	= eventsDetails.ResourceName,
				namespace	= chaosDetails.ChaosNamespace,
				uid		= eventsDetails.ResourceUID,
			), 
			message			= eventsDetails.Message,
			metadata		= client.V1ObjectMeta(
				name	 	= eventName,
				namespace	= chaosDetails.ChaosNamespace,
			), 
			reason			= eventsDetails.Reason, 
			related			= None, 
			action			= "ChaosEvent",
			reporting_component	= "litmuschaos.io/v1alpha1", 
			reporting_instance	= eventsDetails.ResourceName, 
			series			= None, 
   			source			= client.V1EventSource(
				component	= chaosDetails.ChaosPodName,
			), 
			type			= eventsDetails.Type, 
			local_vars_configuration= None,
			count			= 1,
			)
	try:
		clients.clientCoreV1.create_namespaced_event(chaosDetails.ChaosNamespace, body=event)
	except Exception as exp:
		return ValueError("Failed to create event with err: {}".format(exp))
	return None

#GenerateEvents update the events and increase the count by 1, if already present
# else it will create a new event
def GenerateEvents(eventsDetails, chaosDetails, kind, clients):
	
	if kind == "ChaosResult":
		eventName = eventsDetails.Reason + chaosDetails.ChaosPodName	
		err = CreateEvents(eventsDetails, chaosDetails, kind, eventName, clients)
		if err != None:
			return err
	elif kind == "ChaosEngine":
		eventName = eventsDetails.Reason + chaosDetails.ExperimentName + str(chaosDetails.ChaosUID)
		event = client.V1Event
		try:
			event = clients.clientCoreV1.read_namespaced_event(name = eventName,namespace = chaosDetails.ChaosNamespace)
		except Exception as exp:
			if k8serror.K8serror().IsNotFound(err=exp):
				return CreateEvents(eventsDetails, chaosDetails, kind, eventName, clients)
			else:
				return exp
		event.last_timestamp = datetime.now(pytz.utc)
		event.count = event.count + 1
		event.source.component = chaosDetails.ChaosPodName
		event.message = eventsDetails.Message
		try:
			clients.clientCoreV1.patch_namespaced_event(eventName, chaosDetails.ChaosNamespace, body = event)
		except Exception as exp:
			return exp
	return None
