
import pkg.types.types  as types
import pkg.events.events as events
from kubernetes import client, config
import time
import logging
logging.basicConfig(format='time=%(asctime)s level=%(levelname)s  msg=%(message)s', level=logging.INFO)  
import pkg.utils.common.common as common
from pkg.utils.common.pods import Pods
from datetime import datetime
from pkg.status.application import Application
import pkg.maths.maths as maths
import os

#PreparePodDelete contains the prepration steps before chaos injection
def PreparePodDelete(experimentsDetails , resultDetails, eventsDetails, chaosDetails, clients):

	#Waiting for the ramp time before chaos injection
	if experimentsDetails.RampTime != 0 :
		logging.info("[Ramp]: Waiting for the %s ramp time before injecting chaos",(experimentsDetails.RampTime))
		common.WaitForDuration(experimentsDetails.RampTime)
	
	if experimentsDetails.Sequence.lower() == "serial":
		err = injectChaosInSerialMode(experimentsDetails, chaosDetails, eventsDetails, resultDetails, clients)
		if err != None:
			return err
	elif experimentsDetails.Sequence.lower() == "parallel":
		err = injectChaosInParallelMode(experimentsDetails, chaosDetails, eventsDetails, resultDetails, clients)
		if err != None:
			return err
	else:
		logging.warning("[Warning]: %s sequence is not supported",(experimentsDetails.Sequence))

	#Waiting for the ramp time after chaos injection
	if experimentsDetails.RampTime != 0 :
		logging.info("[Ramp]: Waiting for the %s ramp time after injecting chaos",(experimentsDetails.RampTime))
		common.WaitForDuration(experimentsDetails.RampTime)
	return None

# injectChaosInSerialMode delete the target application pods serial mode(one by one)
def injectChaosInSerialMode(experimentsDetails , chaosDetails , eventsDetails , resultDetails, clients): 
	
	status = Application()
	
	pods = Pods()
	GracePeriod = 0
	
	#ChaosStartTimeStamp contains the start timestamp, when the chaos injection begin
	ChaosStartTimeStamp = datetime.now()
	duration = (datetime.now() - ChaosStartTimeStamp).seconds
	
	while duration < experimentsDetails.ChaosDuration:
		# Get the target pod details for the chaos execution
		# if the target pod is not defined it will derive the random target pod list using pod affected percentage
		if experimentsDetails.TargetPods == "" and chaosDetails.AppDetail.Label == "" :
			return logging.warning("[Warning]: Please provide one of the appLabel or TARGET_PODS")
		
		targetPodList, err = pods.GetPodList(experimentsDetails.TargetPods, experimentsDetails.PodsAffectedPerc, chaosDetails, clients)
		if err != None: 
			return err
		
		podNames = []
		for pod in targetPodList.items:
			podNames.append(pod.metadata.name)
		
		logging.info("[Info]: Target pods list, %s",(podNames))

		if experimentsDetails.EngineName != "" :
			msg = "Injecting " + experimentsDetails.ExperimentName + " chaos on application pod"
			types.SetEngineEventAttributes(eventsDetails, types.ChaosInject, msg, "Normal", chaosDetails)
			events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine", clients)
		
		#Deleting the application pod
		for pod in targetPodList.items :

			logging.info("[Info]: Killing the following pods, PodName : %s", pod.metadata.name)
			try:
				if experimentsDetails.Force == True:
					err = clients.clientk8s.delete_namespaced_pod(pod.metadata.name, experimentsDetails.AppNS, grace_period_seconds=GracePeriod)
				else:
					err = clients.clientk8s.delete_namespaced_pod(pod.metadata.name, experimentsDetails.AppNS)
			except Exception as e:
				return e

			if chaosDetails.Randomness == True :
				err = common.RandomInterval(experimentsDetails.ChaosInterval)
				if err != None:
					return err
			else:
				#Waiting for the chaos interval after chaos injection
				if experimentsDetails.ChaosInterval != "":
					logging.info("[Wait]: Wait for the chaos interval %s",(experimentsDetails.ChaosInterval))
					waitTime = maths.atoi(experimentsDetails.ChaosInterval)
					common.WaitForDuration(waitTime)

			#Verify the status of pod after the chaos injection
			logging.info("[Status]: Verification for the recreation of application pod")
			err = status.CheckApplicationStatus(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.Timeout, experimentsDetails.Delay,clients)
			if err != None:
				return err
			
			duration = (datetime.now() - ChaosStartTimeStamp).seconds

	logging.info("[Completion]: %s chaos is done",(experimentsDetails.ExperimentName))

	return None

# injectChaosInParallelMode delete the target application pods in parallel mode (all at once)
def injectChaosInParallelMode(experimentsDetails , chaosDetails , eventsDetails , resultDetails, clients):
	
	status = Application()
	pods = Pods()

	GracePeriod = 0
	
	#ChaosStartTimeStamp contains the start timestamp, when the chaos injection begin
	ChaosStartTimeStamp = datetime.now()
	duration = (datetime.now() - ChaosStartTimeStamp).seconds
	
	while duration < experimentsDetails.ChaosDuration:
		# Get the target pod details for the chaos execution
		# if the target pod is not defined it will derive the random target pod list using pod affected percentage
		if experimentsDetails.TargetPods == "" and chaosDetails.AppDetail.Label == "" :
			return logging.info("[Warning]: Please provide one of the appLabel or TARGET_PODS")
		
		targetPodList, err = pods.GetPodList(experimentsDetails.TargetPods, experimentsDetails.PodsAffectedPerc, chaosDetails, clients)
		if err != None:
			return err
		podNames = []
		for pod in targetPodList.items:
			podNames.append(str(pod.metadata.name))
		
		logging.info("[Info]: Target pods list for chaos, %s",(podNames))
		
		if experimentsDetails.EngineName != "" :
			msg = "Injecting " + experimentsDetails.ExperimentName + " chaos on application pod"
			types.SetEngineEventAttributes(eventsDetails, types.ChaosInject, msg, "Normal", chaosDetails)
			events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine",clients)

		#Deleting the application pod
		for pod in targetPodList.items:
			logging.info("[Info]: Killing the following pods, PodName : %s", pod.metadata.name)
			try:
				if experimentsDetails.Force == True:
					clients.clientk8s.delete_namespaced_pod(pod.metadata.name, experimentsDetails.AppNS, grace_period_seconds=GracePeriod)
				else:
					clients.clientk8s.delete_namespaced_pod(pod.metadata.name, experimentsDetails.AppNS)
			except Exception as err:
				return err	
		
		if chaosDetails.Randomness == True:
			err = common.RandomInterval(experimentsDetails.ChaosInterval)
			if err != None:
				return err
		else:
			#Waiting for the chaos interval after chaos injection
			if experimentsDetails.ChaosInterval != "" :
				logging.info("[Wait]: Wait for the chaos interval %s", experimentsDetails.ChaosInterval)
				waitTime = maths.atoi(experimentsDetails.ChaosInterval)
				common.WaitForDuration(waitTime)

		#Verify the status of pod after the chaos injection
		logging.info("[Status]: Verification for the recreation of application pod")
		err = status.CheckApplicationStatus(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.Timeout, experimentsDetails.Delay, clients)
		if err != None:
			return err
		duration = (datetime.now() - ChaosStartTimeStamp).seconds

	logging.info("[Completion]: %s chaos is done",(experimentsDetails.ExperimentName))

	return None
