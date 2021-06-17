
import pkg.types.types  as types
import pkg.events.events as events
from kubernetes import client, config
import time
import logging
logger = logging.getLogger(__name__)
import pkg.utils.common.common as common
from pkg.utils.common.pods import Pods
from datetime import datetime
from pkg.status.application import Application
import os

global conf
if os.getenv('KUBERNETES_SERVICE_HOST'):
	conf = config.load_incluster_config()
else:
	conf = config.load_kube_config()

#Atoi stands for ASCII to Integer Conversion
def atoi(string):
    res = 0
    # Iterate through all characters of
    #  input and update result
    for i in range(len(string)):
        res = res * 10 + (ord(string[i]) - ord('0'))

    return res

#PreparePodDelete contains the prepration steps before chaos injection
def PreparePodDelete(experimentsDetails , resultDetails, eventsDetails, chaosDetails):

	#Waiting for the ramp time before chaos injection
	if experimentsDetails.RampTime != 0 :
		print("[Ramp]: Waiting for the {} ramp time before injecting chaos".format(experimentsDetails.RampTime))
		common.WaitForDuration(experimentsDetails.RampTime)
	
	if experimentsDetails.Sequence.lower() == "serial":
		err = injectChaosInSerialMode(experimentsDetails, chaosDetails, eventsDetails, resultDetails)
		if err != None:
			return err
	elif experimentsDetails.Sequence.lower() == "parallel":
		err = injectChaosInParallelMode(experimentsDetails, chaosDetails, eventsDetails, resultDetails)
		if err != None:
			return err
	else:
		print("{} sequence is not supported".format(experimentsDetails.Sequence))

	#Waiting for the ramp time after chaos injection
	if experimentsDetails.RampTime != 0 :
		print("[Ramp]: Waiting for the {} ramp time after injecting chaos".format(experimentsDetails.RampTime))
		common.WaitForDuration(experimentsDetails.RampTime)
	return None

# injectChaosInSerialMode delete the target application pods serial mode(one by one)
def injectChaosInSerialMode(experimentsDetails , clients , chaosDetails , eventsDetails , resultDetails): 
	
	status = Application()
	v1 = client.CoreV1Api()
	pods = Pods()

	GracePeriod = 0
	
	#ChaosStartTimeStamp contains the start timestamp, when the chaos injection begin
	ChaosStartTimeStamp = datetime.now()
	duration = (datetime.now() - ChaosStartTimeStamp).seconds
	
	while duration < experimentsDetails.ChaosDuration:
		# Get the target pod details for the chaos execution
		# if the target pod is not defined it will derive the random target pod list using pod affected percentage
		if experimentsDetails.TargetPods == "" and chaosDetails.AppDetail.Label == "" :
			return print("please provide one of the appLabel or TARGET_PODS")
		
		targetPodList, err = pods.GetPodList(experimentsDetails.TargetPods, experimentsDetails.PodsAffectedPerc, chaosDetails)
		if err != None: 
			return err
		
		podNames = []
		for pod in targetPodList.items:
			podNames.append(pod.metadata.name)
		
		print("Target pods list, {}".format(podNames))

		if experimentsDetails.EngineName != "" :
			msg = "Injecting " + experimentsDetails.ExperimentName + " chaos on application pod"
			types.SetEngineEventAttributes(eventsDetails, types.ChaosInject, msg, "Normal", chaosDetails)
			events.GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
		
		#Deleting the application pod
		for pod in targetPodList.items :

			print("[Info]: Killing the following pods", "PodName :", pod.metadata.name)
			try:
				if experimentsDetails.Force == True:
					err = v1.delete_namespaced_pod(pod.metadata.name, experimentsDetails.AppNS, grace_period_seconds=GracePeriod)
				else:
					err = v1.delete_namespaced_pod(pod.metadata.name, experimentsDetails.AppNS)
			except Exception as e:
				return e

			if chaosDetails.Randomness == True :
				err = common.RandomInterval(experimentsDetails.ChaosInterval)
				if err != None:
					return err
			else:
				#Waiting for the chaos interval after chaos injection
				if experimentsDetails.ChaosInterval != "":
					print("[Wait]: Wait for the chaos interval {}".format(experimentsDetails.ChaosInterval))
					waitTime = atoi(experimentsDetails.ChaosInterval)
					common.WaitForDuration(waitTime)

			#Verify the status of pod after the chaos injection
			print("[Status]: Verification for the recreation of application pod")
			err = status.CheckApplicationStatus(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.Timeout, experimentsDetails.Delay)
			if err != None:
				return err
			
			duration = int(time.Since(ChaosStartTimeStamp).Seconds())

	print("[Completion]: {} chaos is done".format(experimentsDetails.ExperimentName))

	return None

# injectChaosInParallelMode delete the target application pods in parallel mode (all at once)
def injectChaosInParallelMode(experimentsDetails  , chaosDetails , eventsDetails , resultDetails):
	
	status = Application()
	v1 = client.CoreV1Api()
	pods = Pods()

	GracePeriod = 0
	
	#ChaosStartTimeStamp contains the start timestamp, when the chaos injection begin
	ChaosStartTimeStamp = datetime.now()
	duration = (datetime.now() - ChaosStartTimeStamp).seconds
	
	while duration < experimentsDetails.ChaosDuration:
		# Get the target pod details for the chaos execution
		# if the target pod is not defined it will derive the random target pod list using pod affected percentage
		if experimentsDetails.TargetPods == "" and chaosDetails.AppDetail.Label == "" :
			return print("please provide one of the appLabel or TARGET_PODS")
		
		targetPodList, err = pods.GetPodList(experimentsDetails.TargetPods, experimentsDetails.PodsAffectedPerc, chaosDetails)
		if err != None:
			return err
		print(len(targetPodList.items))
		podNames = []
		for pod in targetPodList.items:
			podNames.append(str(pod.metadata.name))
		
		print("Target pods list for chaos, {}".format(podNames))
		
		if experimentsDetails.EngineName != "" :
			msg = "Injecting " + experimentsDetails.ExperimentName + " chaos on application pod"
			types.SetEngineEventAttributes(eventsDetails, types.ChaosInject, msg, "Normal", chaosDetails)
			events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine")

		#Deleting the application pod
		for pod in targetPodList.items:
			print(pod.metadata.name)
			print("[Info]: Killing the following pods", "PodName :", pod.metadata.name)
			try:
				if experimentsDetails.Force == True:
					v1.delete_namespaced_pod(pod.metadata.name, experimentsDetails.AppNS, grace_period_seconds=GracePeriod)
				else:
					v1.delete_namespaced_pod(pod.metadata.name, experimentsDetails.AppNS)
			except Exception as err:
				return err	
		
		if chaosDetails.Randomness == True:
			err = common.RandomInterval(experimentsDetails.ChaosInterval)
			if err != None:
				return err
		else:
			#Waiting for the chaos interval after chaos injection
			if experimentsDetails.ChaosInterval != "" :
				print("[Wait]: Wait for the chaos interval %vs", experimentsDetails.ChaosInterval)
				waitTime = atoi(experimentsDetails.ChaosInterval)
				common.WaitForDuration(waitTime)

		#Verify the status of pod after the chaos injection
		print("[Status]: Verification for the recreation of application pod")
		err = status.CheckApplicationStatus(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.Timeout, experimentsDetails.Delay)
		if err != None:
			return err
		duration = (datetime.now() - ChaosStartTimeStamp).seconds

	print("[Completion]: {} chaos is done".format(experimentsDetails.ExperimentName))

	return None
