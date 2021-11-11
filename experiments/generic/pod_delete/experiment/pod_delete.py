import pkg.types.types  as types
import pkg.generic.pod_delete.types.types as experimentDetails
import pkg.generic.pod_delete.environment.environment as experimentEnv
import pkg.events.events as events
import logging
import pkg.status.application as application
import chaosLib.litmus.pod_delete.lib.pod_delete as litmusLIB
import pkg.result.chaosresult as chaosResults
import pkg.utils.common.common as common

# PodDelete inject the pod-delete chaos
def PodDelete(clients):

	# Initialising expermentDetails, resultDetails, eventsDetails, chaosDetails, status and result objects
	experimentsDetails = experimentDetails.ExperimentDetails()
	resultDetails = types.ResultDetails()
	eventsDetails = types.EventDetails()
	chaosDetails = types.ChaosDetails()
	status = application.Application()
	result = chaosResults.ChaosResults()
	
	#Fetching all the ENV passed from the runner pod
	experimentEnv.GetENV(experimentsDetails)
	
	logging.info("[PreReq]: Initialise Chaos Variables for the %s experiment", experimentsDetails.ExperimentName)
	# Intialise the chaos attributes
	experimentEnv.InitialiseChaosVariables(chaosDetails, experimentsDetails)
	
	# Intialise Chaos Result Parameters
	types.SetResultAttributes(resultDetails, chaosDetails)
	
	#Updating the chaos result in the beginning of experiment
	logging.info("[PreReq]: Updating the chaos result of %s experiment (SOT)",(experimentsDetails.ExperimentName))
	err = result.ChaosResult(chaosDetails, resultDetails, "SOT", clients)
	if err != None:
		logging.error("Unable to Create the Chaos Result, err: %s",(err))
		failStep = "Updating the chaos result of pod-delete experiment (SOT)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails, clients)
		return
	
	# Set the chaos result uid
	result.SetResultUID(resultDetails, chaosDetails, clients)
	
	# generating the event in chaosresult to marked the verdict as awaited
	msg = "Experiment " + experimentsDetails.ExperimentName + ", Result Awaited"
	types.SetResultEventAttributes(eventsDetails, types.AwaitedVerdict, msg, "Normal", resultDetails)
	events.GenerateEvents(eventsDetails, chaosDetails, "ChaosResult", clients)

	#DISPLAY THE APP INFORMATION
	logging.info("[Info]: The application information is as follows Namespace=%s, Label=%s, Ramp Time=%s",experimentsDetails.AppNS,experimentsDetails.AppLabel,experimentsDetails.RampTime)
	
	# Calling AbortWatcher, it will continuously watch for the abort signal and generate the required and result
	common.AbortWatcher(experimentsDetails.ExperimentName, resultDetails, chaosDetails, eventsDetails, clients)
	
	# PRE-CHAOS APPLICATION STATUS CHECK
	logging.info("[Status]: Verify that the AUT (Application Under Test) is running (pre-chaos)")
	err = status.AUTStatusCheck(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.TargetContainer, experimentsDetails.Timeout, experimentsDetails.Delay, chaosDetails, clients)
	if err != None:
		logging.error("Application status check failed, err: %s", err)
		failStep = "Verify that the AUT (Application Under Test) is running (pre-chaos)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails, clients)
		return
	
	if experimentsDetails.EngineName != "":
		# marking AUT as running, as we already checked the status of application under test
		msg = "AUT: Running"
		# generating the for the pre-chaos check
		types.SetEngineEventAttributes(eventsDetails, types.PreChaosCheck, msg, "Normal", chaosDetails)
		events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine", clients)
	

	# Including the litmus lib for pod-delete
	if experimentsDetails.ChaosLib == "litmus" :
		err = litmusLIB.PreparePodDelete(experimentsDetails, resultDetails, eventsDetails, chaosDetails, clients)
		if err != None:
			logging.error("Chaos injection failed, err: %s",(err))
			failStep = "failed in chaos injection phase"
			result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails, clients)
			return
		
	else:
		logging.info("[Invalid]: Please Provide the correct LIB")
		failStep = "no match found for specified lib"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails, clients)
		return
	
	logging.info("[Confirmation]: %s chaos has been injected successfully", experimentsDetails.ExperimentName)
	resultDetails.Verdict = "Pass"

	#POST-CHAOS APPLICATION STATUS CHECK
	logging.info("[Status]: Verify that the AUT (Application Under Test) is running (post-chaos)")
	err = status.AUTStatusCheck(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.TargetContainer, experimentsDetails.Timeout, experimentsDetails.Delay, chaosDetails, clients)
	if err != None:
		logging.error("Application status check failed, err: %s", err)
		failStep = "Verify that the AUT (Application Under Test) is running (post-chaos)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails, clients)
		return
	
	if experimentsDetails.EngineName != "" :
		# marking AUT as running, as we already checked the status of application under test
		msg = "AUT: Running"	

		# generating post chaos event
		types.SetEngineEventAttributes(eventsDetails, types.PostChaosCheck, msg, "Normal", chaosDetails)
		events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine", clients)
	

	#Updating the chaosResult in the end of experiment
	logging.info("[The End]: Updating the chaos result of %s experiment (EOT)", experimentsDetails.ExperimentName)
	err = result.ChaosResult(chaosDetails, resultDetails, "EOT", clients)
	if err != None:
		logging.error("Unable to Update the Chaos Result, err: %s", err)
		return
	
	# generating the event in chaosresult to marked the verdict as pass/fail
	msg = "Experiment " + experimentsDetails.ExperimentName + ", Result " + resultDetails.Verdict
	reason = types.PassVerdict
	eventType = "Normal"
	if resultDetails.Verdict != "Pass":
		reason = types.FailVerdict
		eventType = "Warning"

	types.SetResultEventAttributes(eventsDetails, reason, msg, eventType, resultDetails)
	events.GenerateEvents(eventsDetails, chaosDetails, "ChaosResult", clients)
	if experimentsDetails.EngineName != "":
		msg = experimentsDetails.ExperimentName + " experiment has been " + resultDetails.Verdict + "ed"
		types.SetEngineEventAttributes(eventsDetails, types.Summary, msg, "Normal", chaosDetails)
		events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine", clients)
