import pkg.types.types  as types
from pkg.generic.podDelete.types.types import ExperimentDetails
from pkg.generic.podDelete.environment.environment import GetENV, InitialiseChaosVariables
from pkg.events.events import GenerateEvents
from pkg.status.application import Application
import logging
logger = logging.getLogger(__name__)

# PodDelete inject the pod-delete chaos
def PodDelete():
	experimentsDetails = ExperimentDetails()
	resultDetails = types.ResultDetails()
	eventsDetails = types.EventDetails()
	chaosDetails = types.ChaosDetails()
	status = Application()
	
	#Fetching all the ENV passed from the runner pod
	logger.info("[PreReq]: Getting the ENV for the %v experiment", experimentsDetails.ExperimentName)
	GetENV(experimentsDetails)

	# Intialise the chaos attributes
	InitialiseChaosVariables(chaosDetails, experimentsDetails)
	
	# Intialise Chaos Result Parameters
	types.SetResultAttributes(resultDetails, chaosDetails)

	# generating the event in chaosresult to marked the verdict as awaited
	msg = "experiment: " + experimentsDetails.ExperimentName + ", Result: Awaited"
	types.SetResultEventAttributes(eventsDetails, types.AwaitedVerdict, msg, "Normal", resultDetails)
	#GenerateEvents(eventsDetails, chaosDetails, "ChaosResult")

	#DISPLAY THE APP INFORMATION
	print("The application information is as follows", {
		"Namespace": experimentsDetails.AppNS,
		"Label":     experimentsDetails.AppLabel,
		"Ramp Time": experimentsDetails.RampTime,
	})

	# logger.info("[Status]: Verify that the AUT (Application Under Test) is running (pre-chaos)")
	err = status.AUTStatusCheck(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.TargetContainer, experimentsDetails.Timeout, experimentsDetails.Delay, chaosDetails)
	if err != None:
		logger.Errorf("Application status check failed, err: %v", err)
		failStep = "Verify that the AUT (Application Under Test) is running (pre-chaos)"
		return
	
