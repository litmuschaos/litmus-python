
from kubernetes import client
import kubernetes.client
from kubernetes.client.rest import ApiException
from datetime import datetime
from chaosk8s import create_k8s_api_client
configuration = kubernetes.client.Configuration()
from datetime import datetime, timedelta
import pytz
from pkg.utils.k8serror.k8serror import K8serror

#CreateEvents create the events in the desired resource
def CreateEvents(eventsDetails , chaosDetails, kind, eventName):
	api = create_k8s_api_client(secrets = None)
	api_instance = client.CoreV1Api(api)
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
			), reason=eventsDetails.Message, related=None, 
			reporting_component=None, reporting_instance=None, series=None, source=client.V1EventSource(
				component= chaosDetails.ChaosPodName,
			), type=eventsDetails.Type, local_vars_configuration=None,
			count=1,
			)
	print("Let's create event")
	try:
		api_instance.create_namespaced_event(chaosDetails.ChaosNamespace, body)
		print(api_instance)
	except ApiException as e:
		return Exception(e)
	
	return None

#GenerateEvents update the events and increase the count by 1, if already present
# else it will create a new event
def GenerateEvents(eventsDetails, chaosDetails, kind):
	time_stamp = datetime.now(pytz.utc)
	api_instance = client.CoreV1Api()
	api = create_k8s_api_client(secrets = None)
	api_instance = client.CoreV1Api(api)
	
	if kind == "ChaosResult":
		eventName = eventsDetails.Reason + chaosDetails.ChaosPodName
		err = CreateEvents(eventsDetails, chaosDetails, kind, eventName)
		if err != None:
			return err
	elif kind == "ChaosEngine":
		eventName = eventsDetails.Reason + chaosDetails.ExperimentName + str(chaosDetails.ChaosUID)
		event = client.V1Event
		try:
			 event  = api_instance.read_namespaced_event( name = eventName,namespace = chaosDetails.ChaosNamespace)
		except Exception as e:
			if K8serror().IsNotFound(err=e):
				try:
					CreateEvents(eventsDetails, chaosDetails, kind, eventName)
				except Exception as err:
					return err
			return e
		
		event.last_timestamp = time_stamp
		event.count = event.count + 1
		event.source.component = chaosDetails.ChaosPodName
		event.message = eventsDetails.Message
		try:
			api_instance.patch_namespaced_event(eventName, chaosDetails.ChaosNamespace, body = event)
		except ApiException as e:
			return e
		return None
	return None
