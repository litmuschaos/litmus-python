from kubernetes import client, config
import time
from pkg.types.types import ChaosDetails
import logging
from retry import retry
import logging
from pkg.utils.annotation.annotation import IsPodParentAnnotated
logger = logging.getLogger(__name__)


# AUTStatusCheck checks the status of application under test
# if annotationCheck is true, it will check the status of the annotated pod only
# else it will check status of all pods with matching label
class Application(object):
	def __init__(self, appNs=None, appLabel=None, containerName=None, timeout=None, delay=None, clients=None, chaosDetails=None, 
	AuxiliaryAppDetails=None, states=None, duration=None, podName=None , ContainerStatuses=None):
		self.appNs                   = appNs
		self.appLabel                = appLabel
		self.containerName           = containerName
		self.timeout                 = timeout
		self.chaosDetails            = chaosDetails
		self.delay                   = delay
		self.clients                 = clients
		self.states                  = states
		self.AuxiliaryAppDetails     = AuxiliaryAppDetails
		self.duration                = duration             
		self.podName                 = podName
		self.ContainerStatuses       = ContainerStatuses
		self.AnnotatedApplicationsStatusCheck = retry(exceptions=Exception,max_delay=timeout,tries=timeout/delay, delay=delay, backoff=0)(self.AnnotatedApplicationsStatusCheck)
		self.CheckPodStatusPhase = retry(exceptions=Exception,max_delay=timeout,tries=timeout/delay, delay=delay, backoff=0)(self.CheckPodStatusPhase)
		self.CheckContainerStatus = retry(exceptions=Exception,max_delay=timeout,tries=timeout/delay, delay=delay, backoff=0)(self.CheckContainerStatus)
		self.WaitForCompletion = retry(exceptions=Exception,max_delay=timeout,tries=timeout/delay, delay=delay, backoff=0)(self.WaitForCompletion)
		
    
	def AUTStatusCheck(self):

		if self.chaosDetails.AppDetail.AnnotationCheck:
			return self.AnnotatedApplicationsStatusCheck(self.appNs, self.appLabel, self.containerName, self.timeout, self.delay, self.clients, self.chaosDetails)
		else:
			if self.appLabel == "" :
				# Checking whether applications are healthy
				logger.Info("[Status]: No self.appLabels provided, skipping the application status checks")
			else:
				# Checking whether application containers are in ready state
				logger.Info("[Status]: Checking whether application containers are in ready state")
				err = self.CheckContainerStatus(self.appNs, self.appLabel, self.containerName, self.timeout, self.delay, self.clients)
				if err != None:
					return err
				
				# Checking whether application pods are in running state
				logger.Info("[Status]: Checking whether application pods are in running state")
				err = self.CheckPodStatus(self.appNs, self.appLabel, self.timeout, self.delay, self.clients)
				if err != None:
					return err
		return None
	

	#AnnotatedApplicationsStatusCheck checks the status of all the annotated applications with matching label
	def AnnotatedApplicationsStatusCheck(self):
    		
		try:
			try:
				podList = self.clients.CoreV1Api().list_pod_for_all_namespaces(label_selector=self.appLabel)
			except Exception as e:
				return e
			if len(podList.Items) == 0:
				return logger.Errorf("Unable to find the pods with matching labels")
			
			for pod in podList.items:
				isPodAnnotated, err = IsPodParentAnnotated(self.clients, pod, self.chaosDetails)
				if err != None:
					return err
				
				if isPodAnnotated:
					if self.containerName == "":
					
						for _, container in pod.Status.self.ContainerStatuses: 
							if container.State.Terminated == None: 
								return logger.Errorf("container is in terminated state")
							
							if container.Ready == False:
								return logger.Errorf("containers are not yet in running state")
							
							logger.info("[Status]: The Container status are as follows", 
								"container :", container.Name, "Pod :", pod.Name, "Readiness :", container.Ready)
						
					else:
						for container in pod.Status.self.ContainerStatuses:
							if self.containerName == container.Name:
								if container.State.Terminated != None:
									return logger.Errorf("container is in terminated state")
								
								if container.Ready == False:
									return logger.Errorf("containers are not yet in running state")
								
								logger.InfoWithValues("[Status]: The Container status are as follows", "container :", container.Name, "Pod :", pod.Name, "Readiness :", container.Ready)
							
					if pod.Status.Phase != "Running":
						return logger.Errorf("%v pod is not yet in running state", pod.Name)
					
					logger.InfoWithValues("[Status]: The status of Pods are as follows",
						"Pod :", pod.Name, "Status :", pod.Status.Phase)
		except:
			raise Exception
		return None


	# CheckApplicationStatus checks the status of the AUT
	def CheckApplicationStatus(self):

		if self.appLabel == "":
			# Checking whether applications are healthy
			logger.Info("[Status]: No self.appLabels provided, skipping the application status checks")
		else:
			# Checking whether application containers are in ready state
			logger.Info("[Status]: Checking whether application containers are in ready state")
			err = self.CheckContainerStatus(self.appNs, self.appLabel, "", self.timeout, self.delay, self.clients)
			if err != None:
				return err
			
			# Checking whether application pods are in running state
			logger.Info("[Status]: Checking whether application pods are in running state")
			err = self.CheckPodStatus(self.appNs, self.appLabel, self.timeout, self.delay, self.clients); 
			if err != None:
				return err

		return None
	

	# CheckAuxiliaryApplicationStatus checks the status of the Auxiliary applications
	def CheckAuxiliaryApplicationStatus(self):

		AuxiliaryAppInfo = self.AuxiliaryAppDetails.split(",")

		for val in AuxiliaryAppInfo:
			AppInfo = val.split(":")
			err = self.CheckApplicationStatus(AppInfo[0], AppInfo[1], self.timeout, self.delay, self.clients)
			if err != None:
				return err
			
		
		return None
	

	# CheckPodStatusPhase checks the status of the application pod
	def CheckPodStatusPhase(self):
		try:
			try:
				podList = self.clients.CoreV1Api().list_pod_for_all_namespaces(label_selector=self.appLabel)
			except Exception as e:
				return e
			for pod in podList.items:
				isInState = self.isOneOfState(str(pod.Status.Phase), self.states)
				if isInState == False: 
					return logger.Errorf("Pod is not yet in %v state(s)", self.states)
				
				logger.InfoWithValues("[Status]: The status of Pods are as follows", 
					"Pod :", pod.Name, "Status :", pod.Status.Phase)
			
		except:
			raise Exception
		return None


	# isOneOfState check for the string should be present inside given list
	def isOneOfState(self):
		for i in self.states :
			if self.podState == self.states[i]:
				return None
		return False 
	

	# CheckPodStatus checks the running status of the application pod
	def CheckPodStatus(self):
		return self.CheckPodStatusPhase(self.appNs, self.appLabel, self.timeout, self.delay, self.clients, "Running")
	

	# CheckContainerStatus checks the status of the application container
	def CheckContainerStatus(self):

		try:
			try:
				podList = self.clients.CoreV1Api().list_pod_for_all_namespaces(label_selector=self.appLabel)
			except Exception as e:
				return e
			for pod in podList.items:
				if self.containerName == "":
					err = self.validateAllContainerStatus(pod.Name, pod.Status.self.ContainerStatuses)
					if err != None:
						return err
					
				else:
					err = self.validateContainerStatus(self.containerName, pod.Name, pod.Status.self.ContainerStatuses); 
					if err != None:
						return err
		except:
			raise Exception
		return None

	# validateContainerStatus verify that the provided container should be in ready state
	def validateContainerStatus(self):
		for container in self.ContainerStatuses:
			if container.Name == self.containerName:
				if container.State.Terminated != None :
					return logger.Errorf("container is in terminated state")
				
				if container.Ready == False :
					return logger.Errorf("containers are not yet in running state")
				
				logger.InfoWithValues("[Status]: The Container status are as follows", 
					"container :", container.Name, "Pod :", self.podName, "Readiness :", container.Ready)
		return None
	

	# validateAllContainerStatus verify that the all the containers should be in ready state
	def validateAllContainerStatus(self):
		for container in self.ContainerStatuses:
			err = self.validateContainerStatus(container.Name, self.podName, self.ContainerStatuses)
			if err != None:
				return err
		return None
	

	# WaitForCompletion wait until the completion of pod
	def WaitForCompletion(self):
		podStatus = ''
		failedPods = 0
		# It will wait till the completion of target container
		# it will retries until the target container completed or met the self.timeout(chaos duration)
		try:
			try:
				podList = self.clients.CoreV1Api().list_pod_for_all_namespaces(label_selector=self.appLabel)
			except Exception as e:
				return e
			# it will check for the status of helper pod, if it is Succeeded and target container is completed then it will marked it as completed and return
			# if it is still running then it will check for the target container, as we can have multiple container inside helper pod (istio)
			# if the target container is in completed state(ready flag is false), then we will marked the helper pod as completed
			# we will retry till it met the self.timeout(chaos duration)
			failedPods = 0
			for pod in podList.items :
				podStatus = str(pod.Status.Phase)
				logger.Infof("helper pod status: %v", podStatus)
				if podStatus != "Succeeded" & podStatus != "Failed":
					for container in pod.Status.self.ContainerStatuses:
						if container.Name == self.containerName & container.Ready:
							return logger.Errorf("Container is not completed yet")
				
				if podStatus == "Pending" :
					return logger.Errorf("pod is in pending state")
				
				logger.InfoWithValues("[Status]: The running status of Pods are as follows", 
					"Pod :", pod.Name, "Status :", podStatus)
				if podStatus == "Failed":
					failedPods = failedPods + 1
		except:
			raise Exception
		if failedPods > 0:
			return logger.Errorf("pod is in pending state")	
		return None
	

	# CheckHelperStatus checks the status of the helper pod
	# and wait until the helper pod comes to one of the {running,completed} self.states
	def CheckHelperStatus(self):

		try:
			try:
				podList = self.clients.CoreV1Api().list_pod_for_all_namespaces(label_selector=self.appLabel)
			except Exception as e:
				return e
			for  pod in podList.items:
				podStatus = str(pod.Status.Phase)
				if podStatus.lower() == "running" or podStatus.lower() == "succeeded":
					logger.Infof("%v helper pod is in %v state", pod.Name, podStatus)
				else:
					return logger.Errorf("%v pod is in %v state", pod.Name, podStatus)
				
				for container in pod.Status.self.ContainerStatuses:
					if container.State.Terminated & container.State.Terminated.Reason != "Completed" :
						return logger.Errorf("container is terminated with %v reason", container.State.Terminated.Reason)
					
		except:
			raise Exception	
		
		return None
		

