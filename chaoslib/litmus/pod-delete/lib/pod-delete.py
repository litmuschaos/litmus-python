
import pkg.types.types  as types
import pkg.events.events as events
from kubernetes.client.api import core_v1_api
from kubernetes.client.models.v1_event import V1Event
from kubernetes import client, config
import time
#import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
import logging
logger = logging.getLogger(__name__)
from chaosk8s import create_k8s_api_client

#PreparePodDelete contains the prepration steps before chaos injection
def PreparePodDelete(experimentsDetails , clients, resultDetails, eventsDetails, chaosDetails):

	#Waiting for the ramp time before chaos injection
	if experimentsDetails.RampTime != 0 :
		logger.Infof("[Ramp]: Waiting for the %vs ramp time before injecting chaos", experimentsDetails.RampTime)
		common.WaitForDuration(experimentsDetails.RampTime)
	

	if experimentsDetails.Sequence.lower() == "serial":
		err = injectChaosInSerialMode(experimentsDetails, clients, chaosDetails, eventsDetails, resultDetails)
        if err != None:
			return err
		
	elif "parallel":
		err = injectChaosInParallelMode(experimentsDetails, clients, chaosDetails, eventsDetails, resultDetails)
        if err != None:
			return err
	else:
		return logger.Errorf("%v sequence is not supported", experimentsDetails.Sequence)
	

	#Waiting for the ramp time after chaos injection
	if experimentsDetails.RampTime != 0 :
		logger.Infof("[Ramp]: Waiting for the %vs ramp time after injecting chaos", experimentsDetails.RampTime)
		common.WaitForDuration(experimentsDetails.RampTime)
	
	return None


# injectChaosInSerialMode delete the target application pods serial mode(one by one)
def injectChaosInSerialMode(experimentsDetails , clients , chaosDetails , eventsDetails , resultDetails): 

	GracePeriod = 0
	#ChaosStartTimeStamp contains the start timestamp, when the chaos injection begin
	ChaosStartTimeStamp = time.Now()
	duration = int(time.Since(ChaosStartTimeStamp).Seconds())

	while duration < experimentsDetails.ChaosDuration:
		# Get the target pod details for the chaos execution
		# if the target pod is not defined it will derive the random target pod list using pod affected percentage
		if experimentsDetails.TargetPods == "" & chaosDetails.AppDetail.Label == "" :
			return logger.Errorf("please provide one of the appLabel or TARGET_PODS")
		
		targetPodList, err = common.GetPodList(experimentsDetails.TargetPods, experimentsDetails.PodsAffectedPerc, clients, chaosDetails)
		if err != None: 
			return err
		

		podNames = {}
		for _, pod in targetPodList.Items:
			podNames = podNames.update(pod.Name)
		
		logger.Infof("Target pods list, %v", podNames)

		if experimentsDetails.EngineName != "" :
			msg = "Injecting " + experimentsDetails.ExperimentName + " chaos on application pod"
			types.SetEngineEventAttributes(eventsDetails, types.ChaosInject, msg, "Normal", chaosDetails)
			events.GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
		

		#Deleting the application pod
		for pod in targetPodList.items :

			logger.InfoWithValues("[Info]: Killing the following pods", loggerrus.Fields{
				"PodName": pod.Name})

			if experimentsDetails.Force == True:
				err = clients.KubeClient.CoreV1().Pods(experimentsDetails.AppNS).Delete(pod.Name, &v1.DeleteOptions{GracePeriodSeconds: &GracePeriod})
            else:
				err = clients.KubeClient.CoreV1().Pods(experimentsDetails.AppNS).Delete(pod.Name, &v1.DeleteOptions{})
		
			if err != None:
				return err
			if chaosDetails.Randomness == True :
				err = common.RandomInterval(experimentsDetails.ChaosInterval)
				if err != None:
                	return err
			else:
				#Waiting for the chaos interval after chaos injection
				if experimentsDetails.ChaosInterval != "":
					logger.Infof("[Wait]: Wait for the chaos interval %vs", experimentsDetails.ChaosInterval)
					waitTime, _ = strconv.Atoi(experimentsDetails.ChaosInterval)
					common.WaitForDuration(waitTime)
				
			

			#Verify the status of pod after the chaos injection
			logger.Info("[Status]: Verification for the recreation of application pod")
			err = status.CheckApplicationStatus(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.Timeout, experimentsDetails.Delay, clients)
			if err != None:
            	return err
			

			duration = int(time.Since(ChaosStartTimeStamp).Seconds())
		

	
	logger.Infof("[Completion]: %v chaos is done", experimentsDetails.ExperimentName)

	return None



# injectChaosInParallelMode delete the target application pods in parallel mode (all at once)
def injectChaosInParallelMode(experimentsDetails , clients , chaosDetails , eventsDetails , resultDetails):

	# run the probes during chaos
	if len(resultDetails.ProbeDetails) != 0 :
		err = probe.RunProbes(chaosDetails, clients, resultDetails, "DuringChaos", eventsDetails)
        if err != None:
			return err
	GracePeriod = 0
	#ChaosStartTimeStamp contains the start timestamp, when the chaos injection begin
	ChaosStartTimeStamp = time.Now()
	duration = int(time.Since(ChaosStartTimeStamp).Seconds())

	while duration < experimentsDetails.ChaosDuration:
		# Get the target pod details for the chaos execution
		# if the target pod is not defined it will derive the random target pod list using pod affected percentage
		if experimentsDetails.TargetPods == "" & chaosDetails.AppDetail.Label == "" :
			return logger.Errorf("please provide one of the appLabel or TARGET_PODS")
		
		targetPodList, err = common.GetPodList(experimentsDetails.TargetPods, experimentsDetails.PodsAffectedPerc, clients, chaosDetails)
		if err != None:
			return err
		

		podNames = {}
		for pod in targetPodList.Items:
			podNames = podNames.update(pod.Name)
		
		logger.Infof("Target pods list for chaos, %v", podNames)

		if experimentsDetails.EngineName != "" :
			msg = "Injecting " + experimentsDetails.ExperimentName + " chaos on application pod"
			types.SetEngineEventAttributes(eventsDetails, types.ChaosInject, msg, "Normal", chaosDetails)
			events.GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")

		#Deleting the application pod
		for pod in targetPodList.items:
			logger.InfoWithValues("[Info]: Killing the following pods", "PodName :", pod.Name)

			if experimentsDetails.Force:
				err = clients.KubeClient.CoreV1().Pods(experimentsDetails.AppNS).Delete(pod.Name, &v1.DeleteOptions{GracePeriodSeconds: &GracePeriod})
            else:
				err = clients.KubeClient.CoreV1().Pods(experimentsDetails.AppNS).Delete(pod.Name, &v1.DeleteOptions{})
			
			if err != None:
				return err
			
		

		if chaosDetails.Randomness == True:
			if err = common.RandomInterval(experimentsDetails.ChaosInterval)
		else:
			#Waiting for the chaos interval after chaos injection
			if experimentsDetails.ChaosInterval != "" :
				logger.Infof("[Wait]: Wait for the chaos interval %vs", experimentsDetails.ChaosInterval)
				waitTime, _ = strconv.Atoi(experimentsDetails.ChaosInterval)
				common.WaitForDuration(waitTime)
			
		

		#Verify the status of pod after the chaos injection
		logger.Info("[Status]: Verification for the recreation of application pod")
		err = status.CheckApplicationStatus(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.Timeout, experimentsDetails.Delay, clients)
			return err
		
		duration = int(time.Since(ChaosStartTimeStamp).Seconds())
	

	logger.Infof("[Completion]: %v chaos is done", experimentsDetails.ExperimentName)

	return None
