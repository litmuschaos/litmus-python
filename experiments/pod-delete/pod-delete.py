import pkg.types.types  as types
from pkg.generic.podDelete.types import experimentTypes
from pkg.generic.podDelete.environment import GetENV, InitialiseChaosVariables
from pkg.events.events import GenerateEvents
import logging
logger = logging.getLogger(__name__)


# PodDelete inject the pod-delete chaos
def PodDelete(clients):

	experimentsDetails = experimentTypes.ExperimentDetails()
	resultDetails = types.ResultDetails()
	eventsDetails = types.EventDetails()
	chaosDetails = types.ChaosDetails()

	#Fetching all the ENV passed from the runner pod
	logger.info("[PreReq]: Getting the ENV for the %v experiment", experimentsDetails.ExperimentName)
	experimentEnv = GetENV(experimentsDetails)

	# Intialise the chaos attributes
	experimentEnv = InitialiseChaosVariables(chaosDetails, experimentsDetails)

	# Intialise Chaos Result Parameters
	types.SetResultAttributes(resultDetails, chaosDetails)

	# if experimentsDetails.EngineName != "" :
	# 	# Intialise the probe details. Bail out upon error, as we haven't entered exp business logic yet
	# 	err = probe.InitializeProbesInChaosResultDetails(chaosDetails, clients, resultDetails): 
	# 	if err != None {
	# 		logger.Errorf("Unable to initialize the probes, err: %v", err)
	# 		return
	

	#Updating the chaos result in the beginning of experiment
	logger.info("[PreReq]: Updating the chaos result of %v experiment (SOT)", experimentsDetails.ExperimentName)
	err = result.ChaosResult(chaosDetails, clients, resultDetails, "SOT")
	
	if err != None:
    	logger.Errorf("Unable to Create the Chaos Result, err: %v", err)
		failStep = "Updating the chaos result of pod-delete experiment (SOT)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
		return err


	# Set the chaos result uid
	result.SetResultUID(resultDetails, clients, chaosDetails)

	# generating the event in chaosresult to marked the verdict as awaited
	msg = "experiment: " + experimentsDetails.ExperimentName + ", Result: Awaited"
	types.SetResultEventAttributes(eventsDetails, types.AwaitedVerdict, msg, "Normal", resultDetails)
	GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosResult")

	#DISPLAY THE APP INFORMATION
	logger.infolist("The application information is as follows", {
		"Namespace": experimentsDetails.AppNS,
		"Label":     experimentsDetails.AppLabel,
		"Ramp Time": experimentsDetails.RampTime,
	})

	# Calling AbortWatcher go routine, it will continuously watch for the abort signal and generate the required and result
	go common.AbortWatcher(experimentsDetails.ExperimentName, clients, resultDetails, chaosDetails, eventsDetails)

	#PRE-CHAOS APPLICATION STATUS CHECK
	logger.Info("[Status]: Verify that the AUT (Application Under Test) is running (pre-chaos)")
	err = status.AUTStatusCheck(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.TargetContainer, experimentsDetails.Timeout, experimentsDetails.Delay, clients, chaosDetails)
	if err != None:
		logger.Errorf("Application status check failed, err: %v", err)
		failStep = "Verify that the AUT (Application Under Test) is running (pre-chaos)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
		return
	

	if experimentsDetails.EngineName != "":
		# marking AUT as running, as we already checked the status of application under test
		msg = "AUT: Running"

		# run the probes in the pre-chaos check
		if len(resultDetails.ProbeDetails) != 0 :

			err = probe.RunProbes(chaosDetails, clients, resultDetails, "PreChaos", eventsDetails):
			if err != None:
				logger.Errorf("Probe Failed, err: %v", err)
				failStep = "Failed while running probes"
				msg = "AUT: Running, Probes: Unsuccessful"
				types.SetEngineEventAttributes(eventsDetails, types.PreChaosCheck, msg, "Warning", chaosDetails)
				GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
				result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
				return
			
			msg = "AUT: Running, Probes: Successful"
		
		# generating the for the pre-chaos check
		types.SetEngineEventAttributes(eventsDetails, types.PreChaosCheck, msg, "Normal", chaosDetails)
		GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
	

	# Including the litmus lib for pod-delete
	switch (experimentsDetails.ChaosLib) {
	case "litmus":
		err = litmusLIB.PreparePodDelete(experimentsDetails, clients, resultDetails, eventsDetails, chaosDetails)
		if err != None:
			logger.Errorf("Chaos injection failed, err: %v", err)
			failStep = "failed in chaos injection phase"
			result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
			return
		
	case "powerfulseal":
		err = powerfulseal.PreparePodDelete(experimentsDetails, clients, resultDetails, eventsDetails, chaosDetails)
		if err != None:
			logger.Errorf("Chaos injection failed, err: %v", err)
			failStep = "failed in chaos injection phase"
			result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
			return
		
	default:
		logger.Error("[Invalid]: Please Provide the correct LIB")
		failStep = "no match found for specified lib"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
		return
	}

	logger.info("[Confirmation]: %v chaos has been injected successfully", experimentsDetails.ExperimentName)
	resultDetails.Verdict = "Pass"

	#POST-CHAOS APPLICATION STATUS CHECK
	logger.Info("[Status]: Verify that the AUT (Application Under Test) is running (post-chaos)")
	err = status.AUTStatusCheck(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.TargetContainer, experimentsDetails.Timeout, experimentsDetails.Delay, clients, chaosDetails)
    if err != None:
		logger.Errorf("Application status check failed, err: %v", err)
		failStep = "Verify that the AUT (Application Under Test) is running (post-chaos)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
		return
	

	if experimentsDetails.EngineName != "" :
		# marking AUT as running, as we already checked the status of application under test
		msg = "AUT: Running"

		# run the probes in the post-chaos check
		if len(resultDetails.ProbeDetails) != 0 :
			err = probe.RunProbes(chaosDetails, clients, resultDetails, "PostChaos", eventsDetails) 
			if err != None:
				logger.Errorf("Probes Failed, err: %v", err)
				failStep = "Failed while running probes"
				msg = "AUT: Running, Probes: Unsuccessful"
				types.SetEngineEventAttributes(eventsDetails, types.PostChaosCheck, msg, "Warning", chaosDetails)
				GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
				result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
				return
			
			msg = "AUT: Running, Probes: Successful"
		

		# generating post chaos event
		types.SetEngineEventAttributes(eventsDetails, types.PostChaosCheck, msg, "Normal", chaosDetails)
		GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
	

	#Updating the chaosResult in the end of experiment
	logger.info("[The End]: Updating the chaos result of %v experiment (EOT)", experimentsDetails.ExperimentName)
	err = result.ChaosResult(chaosDetails, clients, resultDetails, "EOT")
	if err != None:
		logger.Errorf("Unable to Update the Chaos Result, err: %v", err)
		return


	# generating the event in chaosresult to marked the verdict as pass/fail
	msg = "experiment: " + experimentsDetails.ExperimentName + ", Result: " + resultDetails.Verdict
	reason = types.PassVerdict
	eventType = "Normal"
	if resultDetails.Verdict != "Pass":
		reason = types.FailVerdict
		eventType = "Warning"

	types.SetResultEventAttributes(eventsDetails, reason, msg, eventType, resultDetails)
	GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosResult")

	if experimentsDetails.EngineName != "":
		msg = experimentsDetails.ExperimentName + " experiment has been " + resultDetails.Verdict + "ed"
		types.SetEngineEventAttributes(eventsDetails, types.Summary, msg, "Normal", chaosDetails)
		GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")

