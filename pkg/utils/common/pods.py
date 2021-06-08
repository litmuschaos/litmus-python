from kubernetes import client, config
import time
import random

from kubernetes.client.models.v1_pod_list import V1PodList
from pkg.types.types import ChaosDetails
import logging
from retry import retry
import logging
from pkg.utils.annotation.annotation import IsPodParentAnnotated
logger = logging.getLogger(__name__)
from chaosk8s import create_k8s_api_client

#Adjustment contains rule of three for calculating an integer given another integer representing a percentage
def Adjustment(a, b):
	return (a * b) / 100

# AUTStatusCheck checks the status of application under test
# if annotationCheck is True, it will check the status of the annotated pod only
# else it will check status of all pods with matching label
class Pods(object):
	def __init__(self, namespace=None, podLabel=None, containerName=None, timeout=None, delay=None, clients=None, chaosDetails=None, 
	targetPods=None, duration=None, podName=None , name=None, podList=None, targetContainer=None, appNamespace=None, targetPod=None, nonChaosPods=None, appName=None):
		self.namespace               = namespace
		self.podLabel                = podLabel
		self.containerName           = containerName
		self.timeout                 = timeout
		self.chaosDetails            = chaosDetails
		self.delay                   = delay
		self.clients                 = clients
		self.targetPods              = targetPods
		self.duration                = duration             
		self.podName                 = podName
		self.name      				 = name
		self.podList                 = podList
		self.targetContainer		 = targetContainer
		self.appNamespace    		 = appNamespace
		self.targetPod    			 = targetPod
		self.appName   				 = appName
		self.nonChaosPods  			 = nonChaosPods
		self.DeletePodRetry = retry(exceptions=Exception,max_delay=timeout,tries=timeout/delay, delay=delay, backoff=0)(self.DeletePodRetry)
		self.DeleteAllPodRetry = retry(exceptions=Exception,max_delay=timeout,tries=timeout/delay, delay=delay, backoff=0)(self.DeleteAllPodRetry)
		self.DeleteAllPodRetry = retry(exceptions=Exception,max_delay=timeout,tries=timeout/delay, delay=delay, backoff=0)(self.DeleteAllPodRetry)
	
	def DeletePodRetry(self, podLabel, namespace):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		try:
			podSpec = v1.list_namespaced_pod(namespace, label_selector=podLabel)
			if len(podSpec.items) == 0:
				logging.error("no pods found with matching labels") 
		except:
			logging.error("no pods found with matching labels")
		return None
	
	def DeleteAllPodRetry(self, podLabel, namespace):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		try:
			podSpec = v1.list_namespaced_pod(namespace, label_selector=podLabel)
			if len(podSpec.items) == 0:
				logging.error("no pods found with matching labels") 
		except:
			logging.error("no pods found with matching labels")
		return None
	
	#DeletePod deletes the specified pod and wait until it got terminated
	def DeletePod(self, podName, podLabel, namespace, timeout, delay):
		self.timeout = timeout
		self.delay = delay
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		try:
			v1.delete_namespaced_pod(podName, namespace)
		except Exception as e:
			return False,logger.error("no pod found with matching label, err: %v", e)
		# waiting for the termination of the pod
		return self.DeletePodRetry(podLabel, namespace)
	

	#DeleteAllPod deletes all the pods with matching labels and wait until all the pods got terminated
	def DeleteAllPod(self, podLabel, namespace, timeout, delay):
		self.timeout = timeout
		self.delay = delay
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		try:
			v1.delete_collection_namespaced_pod(namespace, label_selector=podLabel)
		except Exception as e:
			return logger.error("no pod found with matching label, err: %v", e)
		# waiting for the termination of the pod
		return self.DeleteAllPodRetry(podLabel, namespace)

	# GetChaosPodAnnotation will return the annotation on chaos pod
	def GetChaosPodAnnotation(self, podName, namespace):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(podName, namespace)
		except Exception as e:
			return None, e
		return pod.metadata.annotations, None
	

	# GetImagePullSecrets return the imagePullSecrets from the experiment pod
	def GetImagePullSecrets(self, podName, namespace):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(podName, namespace)
		except Exception as e:
			return None, e
		return pod.spec.imagePullSecrets, None
	

	# GetChaosPodResourceRequirements will return the resource requirements on chaos pod
	def GetChaosPodResourceRequirements(self, podName, containerName, namespace):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(podName, namespace)
		except Exception as e:
			return client.V1ResourceRequirements, e 
		
		for  container in pod.spec.containers:
			# The name of chaos container is always same as job name
			# <experiment-name>-<runid>
			if container.name == containerName:
				return container.resources, None
		
		return client.V1ResourceRequirements, logger.error("No container found with %v name in target pod", self.containerName)
	

	# VerifyExistanceOfPods check the availibility of list of pods
	def VerifyExistanceOfPods(self, namespace, pods):

		if self.pods == "":
			return False, None
		podList = pods.split(",")
		for index in podList:
			isPodsAvailable, err = self.CheckForAvailibiltyOfPod(namespace, podList[index])
			if err != None :
				return False, err			
			if isPodsAvailable == False:
				return isPodsAvailable, None

		return True, None
	

	#GetPodList check for the availibilty of the target pod for the chaos execution
	# if the target pod is not defined it will derive the random target pod list using pod affected percentage
	def GetPodList(self, targetPods , podAffPerc , chaosDetails):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		realpods = client.V1PodList()
		try:
			podList = v1.list_namespaced_pod(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
		except Exception as e:
			return client.V1PodList, e
		if len(podList.items) == 0:
    			return False,logger.error("Failed to find the pod with matching labels in {} namespace", chaosDetails.AppDetail.Namespace)
		
		isPodsAvailable, err = self.VerifyExistanceOfPods(chaosDetails.AppDetail.Namespace, targetPods)
		if err != None:
			return client.V1PodList, err
		
		# getting the pod, if the target pods is defined
		# else select a random target pod from the specified labels
		if isPodsAvailable == True:
			podList, err = self.GetTargetPodsWhenTargetPodsENVSet(targetPods, chaosDetails)
			if err != None:
				return client.V1PodList, err
			
			realpods.items = realpods.items.append(podList.items)
		else:
			nonChaosPods = self.FilterNonChaosPods(podList, chaosDetails)
			realpods, err = self.GetTargetPodsWhenTargetPodsENVNotSet(podAffPerc, nonChaosPods, chaosDetails)
			if err != None:
				return client.V1PodList, err
		logger.info("[Chaos]:Number of pods targeted: %v", len(realpods.items))
		return realpods, None
	

	# CheckForAvailibiltyOfPod check the availibility of the specified pod
	def CheckForAvailibiltyOfPod(self, namespace, name): 
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		if name == "" :
			return False, None
		try:
			v1.read_namespaced_pod(name, namespace)
		except Exception as e:
			return False, e 
		
		return True, None
	

	#FilterNonChaosPods remove the chaos pods(operator, runner) for the podList
	# it filter when the applabels are not defined and it will select random pods from appns
	def FilterNonChaosPods(self, podList, chaosDetails):
		if chaosDetails.AppDetail.Label == "":
			nonChaosPods = V1PodList
			# ignore chaos pods
			for index, pod in podList.items:
				if (pod.Labels["chaosUID"] != str(chaosDetails.ChaosUID) or pod.Labels["name"] == "chaos-operator"):
					nonChaosPods = nonChaosPods.update(podList.items[index])
					
			return nonChaosPods
		return podList
	

	# GetTargetPodsWhenTargetPodsENVSet derive the specific target pods, if TARGET_PODS env is set
	def GetTargetPodsWhenTargetPodsENVSet(self, targetPods, chaosDetails):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			podList = v1.list_namespaced_pod(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
		except Exception as e:
			return V1PodList, e
		
		if len(podList.items) == 0 :
			return V1PodList,logger.error("Failed to find the pods with matching labels in {} namespace", chaosDetails.AppDetail.Namespace)


		targetPodsList = targetPods.split(",")
		realPods = V1PodList

		for pod in podList.items :
			for index in targetPodsList :
				if targetPodsList[index] == pod.name :
					if chaosDetails.AppDetail.AnnotationCheck == True:
						isPodAnnotated, err = IsPodParentAnnotated(pod, chaosDetails)
						if err != None :
							return V1PodList, err
						
						if isPodAnnotated == False:
							return V1PodList,logger.error("%v target pods are not annotated", targetPods)


					realPods = realPods.update(pod)

		
		return realPods, None
	

	# GetTargetPodsWhenTargetPodsENVNotSet derives the random target pod list, if TARGET_PODS env is not set
	def GetTargetPodsWhenTargetPodsENVNotSet(self, podAffPerc , nonChaosPods, chaosDetails):
		filteredPods = V1PodList
		realPods = V1PodList

		if chaosDetails.AppDetail.AnnotationCheck == True:
			for  pod in nonChaosPods.items:
				isPodAnnotated, err = IsPodParentAnnotated(pod, chaosDetails)
				if err != None:
					return V1PodList, err
				
				if isPodAnnotated == True:
					filteredPods.items = filteredPods.update(pod)
				
			
			if len(filteredPods) == 0:
				return filteredPods,logger.error("No annotated target pod found")
			
		else:
			filteredPods = nonChaosPods
		

		newPodListLength = max(1, Adjustment(podAffPerc, len(filteredPods)))
		#rand.Seed(time.Now().UnixNano())

		# it will generate the random podlist
		# it starts from the random index and choose requirement no of pods next to that index in a circular way.
		index = random.randint(0,filteredPods.items)
		for i in newPodListLength:
			realPods = realPods.update(filteredPods.items[index])
			index = (index + 1) % len(filteredPods.items)
		
		return realPods, None


	# DeleteHelperPodBasedOnJobCleanupPolicy deletes specific helper pod based on jobCleanupPolicy
	def DeleteHelperPodBasedOnJobCleanupPolicy(self, podName, podLabel, chaosDetails):

		if chaosDetails.JobCleanupPolicy == "delete":
			logger.info("[Cleanup]: Deleting %v helper pod", podName)
			err = self.DeletePod(podName, podLabel, chaosDetails.ChaosNamespace, chaosDetails.Timeout, chaosDetails.Delay)
			if err != None:
				logger.error("Unable to delete the helper pod, err: %v", err)

	# DeleteAllHelperPodBasedOnJobCleanupPolicy delete all the helper pods w/ matching label based on jobCleanupPolicy
	def DeleteAllHelperPodBasedOnJobCleanupPolicy(self, podLabel, chaosDetails):

		if chaosDetails.JobCleanupPolicy == "delete":
			logger.Info("[Cleanup]: Deleting all the helper pods")
			err = self.DeleteAllPod(podLabel, chaosDetails.ChaosNamespace, chaosDetails.Timeout, chaosDetails.Delay)
			if err != None :
				logger.error("Unable to delete the helper pods, err: %v", err)

	# GetServiceAccount derive the serviceAccountName for the helper pod
	def GetServiceAccount(self, chaosNamespace, chaosPodName):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(chaosPodName, chaosNamespace)
		except Exception as e:
			return "", e
		
		return pod.spec.serviceAccountName, None


	#GetTargetContainer will fetch the container name from application pod
	#This container will be used as target container
	def GetTargetContainer(self, appNamespace, appName):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(appName, appNamespace)
		except Exception as e:
			return "", e
		
		return pod.spec.containers[0].name, None


	#GetContainerID  derive the container id of the application container
	def GetContainerID(self, appNamespace, targetPod, targetContainer):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(targetPod, appNamespace)
		except Exception as e:
			return e
		
		containerID = ''
		
		# filtering out the container id from the details of containers inside containerStatuses of the given pod
		# container id is present in the form of <runtime>:#<container-id>
		for container in pod.Status.ContainerStatuses:
			if container.name == targetContainer:
				containerID = container.ContainerID.split("//")[1]
				break

		logger.info("container ID of %v container, containerID: %v", targetContainer, containerID)
		return containerID, None
	

	# CheckContainerStatus checks the status of the application container
	def CheckContainerStatus(self, appNamespace, appName):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		
		try:
			try:
				pod = v1.read_namespaced_pod(appName, appNamespace)
			except Exception as e:
				return logger.error("unable to find the pod with name :", appName), e
		
			for container in pod.status.containerStatuses:
				if container.Ready == False:
					return logger.error("containers are not yet in running state")
				logger.InfoWithValues("The running status of container are as follows",
					"container :", container.Name, "Pod :", pod.Name, "Status :", pod.Status.Phase)
			return None
		except Exception as e:
			return e
