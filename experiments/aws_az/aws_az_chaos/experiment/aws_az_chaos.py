import pkg.types.types  as types
import pkg.aws_az.types.types as experimentDetails
import pkg.aws_az.environment.environment as experimentEnv
import pkg.events.events as events
import logging
import chaosLib.litmus.aws_az_chaos.lib.aws_az_chaos as litmusLIB
import pkg.result.chaosresult as chaosResults
import pkg.utils.common.common as common
import pkg.aws_status.status as awsStatus

# AwsAzExperiment contains steps to inject chaos
def AwsAzExperiment(clients):

	# Initialising expermentDetails, resultDetails, eventsDetails, chaosDetails, status and result objects
	experimentsDetails = experimentDetails.ExperimentDetails()
	resultDetails = types.ResultDetails()
	eventsDetails = types.EventDetails()
	chaosDetails = types.ChaosDetails()
	result = chaosResults.ChaosResults()
	statusAws = awsStatus.AWS_AZ()

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
		failStep = "Updating the chaos result of aws-az-chaos experiment (SOT)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails, clients)
		return
	
	# Set the chaos result uid
	result.SetResultUID(resultDetails, chaosDetails, clients)
	
	# generating the event in chaosresult to marked the verdict as awaited
	msg = "Experiment " + experimentsDetails.ExperimentName + ", Result Awaited"
	types.SetResultEventAttributes(eventsDetails, types.AwaitedVerdict, msg, "Normal", resultDetails)
	events.GenerateEvents(eventsDetails, chaosDetails, "ChaosResult", clients)

	# DISPLAY THE LOADBALANCER INFORMATION
	logging.info("[Info]: The application information is as follows LoadBalancer Name=%s, LoadBalancer Zones=%s, Ramp Time=%s",experimentsDetails.LoadBalancerName,experimentsDetails.LoadBalancerZones,experimentsDetails.RampTime)
	
	# Calling AbortWatcher, it will continuously watch for the abort signal and generate the required and result
	common.AbortWatcher(experimentsDetails.ExperimentName, resultDetails, chaosDetails, eventsDetails, clients)

	# PRE-CHAOS APPLICATION STATUS CHECK
	logging.info("[Status]: Verify that the AUT (Application Under Test) is running (pre-chaos)")
	err = statusAws.CheckAWSStatus(experimentsDetails)
	if err != None:
		logging.error("Target available zone status check failed, err: %s", err)
		failStep = "Verify that the AUT (Application Under Test) is running (pre-chaos)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails, clients)
		return

	if experimentsDetails.EngineName != "":
		# marking AUT as running, as we already checked the status of application under test
		msg = "AUT: Running"
		# generating the for the pre-chaos check
		types.SetEngineEventAttributes(eventsDetails, types.PreChaosCheck, msg, "Normal", chaosDetails)
		events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine", clients)
	
	# Including the litmus lib for aws-az-chaos
	if experimentsDetails.ChaosLib == "litmus" :
		err = litmusLIB.PrepareAWSAZExperiment(experimentsDetails, resultDetails, eventsDetails, chaosDetails, clients, statusAws)
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

	# POST-CHAOS APPLICATION STATUS CHECK
	logging.info("[Status]: Verify that the AUT (Application Under Test) is running (post-chaos)")
	err = statusAws.CheckAWSStatus(experimentsDetails)
	if err != None:
		logging.error("Target aws instance status check failed, err: %s", err)
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