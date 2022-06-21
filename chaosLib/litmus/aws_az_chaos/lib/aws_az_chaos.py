
import pkg.utils.common.common as common
import pkg.types.types  as types
import pkg.events.events as events
import logging
from datetime import datetime
import pkg.maths.maths as maths

#PrepareAWSAZExperiment contains the prepration steps before chaos injection
def PrepareAWSAZExperiment(experimentsDetails , resultDetails, eventsDetails, chaosDetails, clients, statusAws):

	# Waiting for the ramp time before chaos injection
	if experimentsDetails.RampTime != 0 :
		logging.info("[Ramp]: Waiting for the %s ramp time before injecting chaos",experimentsDetails.RampTime)
		common.WaitForDuration(experimentsDetails.RampTime)
	
 	# mode for chaos injection
	if experimentsDetails.Sequence.lower() == "serial":
		err = injectChaosInSerialMode(experimentsDetails, chaosDetails, eventsDetails, resultDetails, clients, statusAws)
		if err != None:
			return err
	elif experimentsDetails.Sequence.lower() == "parallel":
		err = injectChaosInParallelMode(experimentsDetails, chaosDetails, eventsDetails, resultDetails, clients, statusAws)
		if err != None:
			return err
	else:
		return ValueError("{} sequence is not supported".format(experimentsDetails.Sequence))

	# Waiting for the ramp time after chaos injection
	if experimentsDetails.RampTime != 0 :
		logging.info("[Ramp]: Waiting for the %s ramp time after injecting chaos",experimentsDetails.RampTime)
		common.WaitForDuration(experimentsDetails.RampTime)

	return None

# injectChaosInSerialMode disable the target available zone from loadbalancer in serial mode(one by one)
def injectChaosInSerialMode(experimentsDetails , chaosDetails , eventsDetails , resultDetails, clients, statusAws): 
	
	#ChaosStartTimeStamp contains the start timestamp, when the chaos injection begin
	ChaosStartTimeStamp = datetime.now()
	duration = (datetime.now() - ChaosStartTimeStamp).seconds
	
	while duration < experimentsDetails.ChaosDuration:
     
		# Get the target available zones for the chaos execution
		targetZones = experimentsDetails.LoadBalancerZones.split(",")
		
		logging.info("[Info]: Target available zone list, %s", targetZones)

		if experimentsDetails.EngineName != "" :
			msg = "Injecting " + experimentsDetails.ExperimentName + " chaos on available zone"
			types.SetEngineEventAttributes(eventsDetails, types.ChaosInject, msg, "Normal", chaosDetails)
			events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine", clients)
		
		# Detaching the target zones from loa balancer 
		for azone in targetZones:

			logging.info("[Info]: Detaching the following zone, Zone Name %s", azone)
			targetSubnet, err = statusAws.getTargetSubnet(experimentsDetails, azone)
			subnetList = list(targetSubnet.split(" "))
			if err != None:
				return err
			logging.info("[Info]: Detaching the following subnet, %s", subnetList)
			err = statusAws.detachSubnet(experimentsDetails, subnetList)
			if err != None:
				return err

			if chaosDetails.Randomness:
				err = common.RandomInterval(experimentsDetails.ChaosInterval)
				if err != None:
					return err
			else:
				#Waiting for the chaos interval after chaos injection
				if experimentsDetails.ChaosInterval != "":
					logging.info("[Wait]: Wait for the chaos interval %s",(experimentsDetails.ChaosInterval))
					waitTime = maths.atoi(experimentsDetails.ChaosInterval)
					common.WaitForDuration(waitTime)

			# Attaching the target available zone after the chaos injection
			logging.info("[Status]: Attach the available zone back to load balancer")
			err = statusAws.attachAZtoLB(experimentsDetails, azone)
			if err != None:
				return err
			
   			#Verify the status of available zone after the chaos injection
			logging.info("[Status]: Checking AWS load balancer's AZ status")		
			err = statusAws.CheckAWSStatus(experimentsDetails)
			if err != None:
				return err
			
			duration = (datetime.now() - ChaosStartTimeStamp).seconds

	logging.info("[Completion]: %s chaos is done",(experimentsDetails.ExperimentName))
	return None

# injectChaosInParallelMode disable the target available zone from loadbalancer in parallel mode (all at once)
def injectChaosInParallelMode(experimentsDetails , chaosDetails , eventsDetails , resultDetails, clients, statusAws):
	
	#ChaosStartTimeStamp contains the start timestamp, when the chaos injection begin
	ChaosStartTimeStamp = datetime.now()
	duration = (datetime.now() - ChaosStartTimeStamp).seconds
	subnet = []

	while duration < experimentsDetails.ChaosDuration:
  		# Get the target available zone details for the chaos execution
		targetZones = experimentsDetails.LoadBalancerZones.split(",")
		logging.info("[Info]: Target available zone list, %s", targetZones)
			
		if experimentsDetails.EngineName != "" :
			msg = "Injecting " + experimentsDetails.ExperimentName + " chaos on available zone"
			types.SetEngineEventAttributes(eventsDetails, types.ChaosInject, msg, "Normal", chaosDetails)
			events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine",clients)
		
		# Detaching the target zones from load balancer
		for azone in targetZones:
			logging.info("[Info]: Detaching the following zone, Zone Name %s", azone)
			targetSubnet, err = statusAws.getTargetSubnet(experimentsDetails, azone)
			subnet.append(targetSubnet)
			if err != None:
				return err
		logging.info("[Info]: Detaching the following subnet(s), %s", subnet)
		err = statusAws.detachSubnet(experimentsDetails,subnet)
		if err != None:
			return err
		
		if chaosDetails.Randomness:
			err = common.RandomInterval(experimentsDetails.ChaosInterval)
			if err != None:
				return err
		else:
			#Waiting for the chaos interval after chaos injection
			if experimentsDetails.ChaosInterval != "" :
				logging.info("[Wait]: Wait for the chaos interval %s", experimentsDetails.ChaosInterval)
				waitTime = maths.atoi(experimentsDetails.ChaosInterval)
				common.WaitForDuration(waitTime)

		# Attaching the target available zone after the chaos injection
		logging.info("[Status]: Attach the available zone back to load balancer")
		for azone in targetZones:
			err = statusAws.attachSubnet(experimentsDetails, subnet)
			if err != None:
				return err
     		
		#Verify the status of available zone after the chaos injection
		logging.info("[Status]: Checking AWS load balancer's AZ status")		
		err = statusAws.CheckAWSStatus(experimentsDetails)
		if err != None:
			return err

		duration = (datetime.now() - ChaosStartTimeStamp).seconds

	logging.info("[Completion]: %s chaos is done",(experimentsDetails.ExperimentName))

	return None
