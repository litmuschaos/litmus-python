
from kubernetes import client, config
import kubernetes.client
from kubernetes.client.rest import ApiException
from datetime import datetime
configuration = kubernetes.client.Configuration()
from datetime import datetime
import pytz
from pkg.utils.k8serror.k8serror import K8serror
import os
import logging
logging.basicConfig(format='time=%(asctime)s level=%(levelname)s  msg=%(message)s', level=logging.INFO) 

global conf
if os.getenv('KUBERNETES_SERVICE_HOST'):
	conf = config.load_incluster_config()
else:
	conf = config.load_kube_config()

#CreateEvents create the events in the desired resource
def CreateEvents(eventsDetails , chaosDetails, kind, eventName, clients):
	
	first_timestamp = datetime.now(pytz.utc)
	last_timestamp = datetime.now(pytz.utc)
	event_time = datetime.now(pytz.utc)
	body = client.V1Event(
			first_timestamp = first_timestamp,
			last_timestamp =  last_timestamp,
			event_time = event_time,
			involved_object= client.V1ObjectReference(
				api_version= "litmuschaos.io/v1alpha1",
				kind     		= kind,
				name     		= eventsDetails.ResourceName,
				namespace		= chaosDetails.ChaosNamespace,
				uid				= eventsDetails.ResourceUID,
			), message= eventsDetails.Message,
			metadata=client.V1ObjectMeta(
				name = eventName,
				namespace= chaosDetails.ChaosNamespace,
			), reason=eventsDetails.Reason, related=None, action="ChaosResult",
			reporting_component="litmuschaos.io/v1alpha1", reporting_instance=eventsDetails.ResourceName, series=None, source=client.V1EventSource(
				component= chaosDetails.ChaosPodName,
			), type=eventsDetails.Type, local_vars_configuration=None,
			count=1,
			)
	try:
		clients.clientk8s.create_namespaced_event(chaosDetails.ChaosNamespace, body=body)
	except Exception as exp:
		return logging.error("Failed to create event with err: %s", exp)
	return None

#GenerateEvents update the events and increase the count by 1, if already present
# else it will create a new event
def GenerateEvents(eventsDetails, chaosDetails, kind, clients):
	
	time_stamp = datetime.now(pytz.utc)
	
	if kind == "ChaosResult":
		eventName = eventsDetails.Reason + chaosDetails.ChaosPodName	
		err = CreateEvents(eventsDetails, chaosDetails, kind, eventName, clients)
		if err != None:
			return err
	elif kind == "ChaosEngine":
		eventName = eventsDetails.Reason + chaosDetails.ExperimentName + str(chaosDetails.ChaosUID)
		event = client.V1Event
		try:
			 event = clients.clientk8s.read_namespaced_event(name = eventName,namespace = chaosDetails.ChaosNamespace)
		except Exception as e:
			if K8serror().IsNotFound(err=e):
				try:
					err = CreateEvents(eventsDetails, chaosDetails, kind, eventName, clients)
					if err != None:
						return err
				except Exception as err:
					return err
			return e
		
		event.last_timestamp = time_stamp
		event.count = event.count + 1
		event.source.component = chaosDetails.ChaosPodName
		event.message = eventsDetails.Message
		try:
			clients.clientk8s.patch_namespaced_event(eventName, chaosDetails.ChaosNamespace, body = event)
		except ApiException as e:
			return e
	return None
