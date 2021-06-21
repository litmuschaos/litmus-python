from kubernetes import client, config
import random
import os
from kubernetes.client.models.v1_pod_list import V1PodList
import logging
from pkg.utils.annotation.annotation import IsPodParentAnnotated
logging.basicConfig(format='time=%(asctime)s level=%(levelname)s  msg=%(message)s', level=logging.INFO)  
from pkg.utils.k8serror.k8serror import K8serror
import sys
import pkg.maths.maths as maths
sys.stdout.flush()

# AUTStatusCheck checks the status of application under test
# if annotationCheck is True, it will check the status of the annotated pod only
# else it will check status of all pods with matching label
class Pods(object):
	def __init__(self, namespace=None, podLabel=None, containerName=None, timeout=None, delay=None, clients=None, chaosDetails=None, 
	targetPods=None, duration=None, podName=None , name=None, podList=None, targetContainer=None, appNamespace=None, targetPod=None, nonChaosPods=None, appName=None):
		self.namespace				= namespace
		self.podLabel				= podLabel
		self.containerName			= containerName
		self.timeout 				= timeout
		self.chaosDetails         	= chaosDetails
		self.delay                 	= delay
		self.clients               	= clients
		self.targetPods            	= targetPods
		self.duration              	= duration             
		self.podName               	= podName
		self.name 					= name
		self.podList               	= podList
		self.targetContainer		= targetContainer
		self.appNamespace    		= appNamespace
		self.targetPod    			= targetPod
		self.appName   				= appName
		self.nonChaosPods  			= nonChaosPods
	
	def DeletePodRetry(self, podLabel, namespace):
		v1=client.CoreV1Api()
		try:
			podSpec = v1.list_namespaced_pod(namespace, label_selector=podLabel)
			if len(podSpec.items) == 0:
				logging.error("no pods found with matching labels") 
		except:
			logging.error("no pods found with matching labels")
		return None
	
	def DeleteAllPodRetry(self, podLabel, namespace):
		v1=client.CoreV1Api()
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
		global conf
		v1=client.CoreV1Api()
		try:
			v1.delete_namespaced_pod(podName, namespace)
		except Exception as e:
			return False,logging.error("no pod found with matching label, err: %s", e)
		# waiting for the termination of the pod
		return self.DeletePodRetry(podLabel, namespace)
	

	#DeleteAllPod deletes all the pods with matching labels and wait until all the pods got terminated
	def DeleteAllPod(self, podLabel, namespace, timeout, delay):
		self.timeout = timeout
		self.delay = delay
		v1=client.CoreV1Api()
		try:
			v1.delete_collection_namespaced_pod(namespace, label_selector=podLabel)
		except Exception as e:
			return logging.error("no pod found with matching label, err: %s", e)
		# waiting for the termination of the pod
		return self.DeleteAllPodRetry(podLabel, namespace)

	# GetChaosPodAnnotation will return the annotation on chaos pod
	def GetChaosPodAnnotation(self, podName, namespace):
		v1=client.CoreV1Api()
		
		try:
			pod = v1.read_namespaced_pod(podName, namespace)
		except Exception as e:
			return None, e
		return pod.metadata.annotations, None
	

	# GetImagePullSecrets return the imagePullSecrets from the experiment pod
	def GetImagePullSecrets(self, podName, namespace):
		v1 = client.CoreV1Api()
		
		try:
			pod = v1.read_namespaced_pod(podName, namespace)
		except Exception as e:
			return None, e
		return pod.spec.image_pull_secrets, None
	
	# GetChaosPodResourceRequirements will return the resource requirements on chaos pod
	def GetChaosPodResourceRequirements(self, podName, containerName, namespace):
		v1 = client.CoreV1Api()
		
		try:
			pod = v1.read_namespaced_pod(podName, namespace)
		except Exception as e:
			return client.V1ResourceRequirements, e 
		
		for  container in pod.spec.containers:
			# The name of chaos container is always same as job name
			# <experiment-name>-<runid>
			if container.name == containerName:
				return container.resources, None
		
		return client.V1ResourceRequirements, logging.error("No container found with %s name in target pod", self.containerName)
	

	# VerifyExistanceOfPods check the availibility of list of pods
	def VerifyExistanceOfPods(self, namespace, pods, clients):

		if pods == "":
			return False, None
		podList = pods.split(",")
		for pod in podList:
			isPodsAvailable, err = self.CheckForAvailibiltyOfPod(namespace, pod, clients)
			if err != None :
				return False, err			
			if isPodsAvailable == False:
				return isPodsAvailable, None

		return True, None
	

	#GetPodList check for the availibilty of the target pod for the chaos execution
	# if the target pod is not defined it will derive the random target pod list using pod affected percentage
	def GetPodList(self, targetPods , podAffPerc , chaosDetails, clients):
		
		realpods = client.V1PodList
		
		try:
			podList = clients.clientk8s.list_namespaced_pod(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
		except Exception as e:
			return client.V1PodList, e
		if len(podList.items) == 0:
    			return False,logging.warning("Failed to find the pod with matching labels in %s namespace", chaosDetails.AppDetail.Namespace)
		isPodsAvailable, err = self.VerifyExistanceOfPods(chaosDetails.AppDetail.Namespace, targetPods, clients)
		if err != None:
			return client.V1PodList, err
		# getting the pod, if the target pods is defined
		# else select a random target pod from the specified labels
		if isPodsAvailable == True:
			realpods, err = self.GetTargetPodsWhenTargetPodsENVSet(targetPods, chaosDetails, clients)
			if err != None or len(realpods.items) == 0:
				return client.V1PodList, err
		else:
			nonChaosPods = self.FilterNonChaosPods(podList, chaosDetails, clients)
			realpods, err = self.GetTargetPodsWhenTargetPodsENVNotSet(podAffPerc, nonChaosPods, chaosDetails, clients)
			if err != None or len(realpods.items) == 0:
				return client.V1PodList, err
		logging.info("[Chaos]:Number of pods targeted: %s",(len(realpods.items)))
		return realpods, None
	

	# CheckForAvailibiltyOfPod check the availibility of the specified pod
	def CheckForAvailibiltyOfPod(self, namespace, name, clients): 
		
		if name == "" :
			return False, None
		try:
			clients.clientk8s.read_namespaced_pod(name, namespace)
		except Exception as err:
			if K8serror().IsNotFound(err) == False:
				return False, err
			elif K8serror().IsNotFound(err):
				return False, None

		return True, None
	

	#FilterNonChaosPods remove the chaos pods(operator, runner) for the podList
	# it filter when the applabels are not defined and it will select random pods from appns
	def FilterNonChaosPods(self, podList, chaosDetails, clients):
		if chaosDetails.AppDetail.Label == "":
			nonChaosPods = []
			# ignore chaos pods
			for pod in podList.items:
				if (pod.metadata.labels["chaosUID"] != str(chaosDetails.ChaosUID) or pod.metadata.labels["name"] == "chaos-operator"):
					nonChaosPods = nonChaosPods.append(pod)
			return V1PodList(items=nonChaosPods)
		return podList
	

	# GetTargetPodsWhenTargetPodsENVSet derive the specific target pods, if TARGET_PODS env is set
	def GetTargetPodsWhenTargetPodsENVSet(self, targetPods, chaosDetails, clients):
		
		try:
			podList = clients.clientk8s.list_namespaced_pod(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
		except Exception as e:
			return V1PodList, e
		
		if len(podList.items) == 0 :
			return V1PodList, logging.error("Failed to find the pods with matching labels in %s namespace", chaosDetails.AppDetail.Namespace), 0

		targetPodsList = targetPods.split(",")
		realPodList = []
		for pod in podList.items :
			for podTarget in targetPodsList :
				if podTarget == pod.metadata.name :
					if chaosDetails.AppDetail.AnnotationCheck == True:
						isPodAnnotated, err = IsPodParentAnnotated(pod, chaosDetails, clients)
						if err != None :
							return V1PodList, err
						
						if isPodAnnotated == False:
							return V1PodList, logging.error("%s target pods are not annotated",(targetPods))

					#realPods.items.append(pod)
					realPodList.append(pod)
					
		return client.V1PodList(items=realPodList), None
	

	# GetTargetPodsWhenTargetPodsENVNotSet derives the random target pod list, if TARGET_PODS env is not set
	def GetTargetPodsWhenTargetPodsENVNotSet(self, podAffPerc , nonChaosPods, chaosDetails, clients):
		filteredPods = []
		realPods = []
		if chaosDetails.AppDetail.AnnotationCheck == True:
			for pod in nonChaosPods.items:
				isPodAnnotated, err = IsPodParentAnnotated(pod, chaosDetails, clients)
				if err != None:
					return V1PodList, err 
				
				if isPodAnnotated == True:
					filteredPods.append(pod)
				
			
			if len(filteredPods) == 0:
				return V1PodList(items=filteredPods), logging.error("No annotated target pod found")
			
		else:
			for pod in nonChaosPods.items:
				filteredPods.append(pod)
		

		newPodListLength = max(1, maths.Adjustment(podAffPerc, len(filteredPods)))
		#rand.Seed(time.Now().UnixNano())

		# it will generate the random podlist
		# it starts from the random index and choose requirement no of pods next to that index in a circular way.
		index = random.randint(0,len(filteredPods)-1)
		for i in range(newPodListLength):
			realPods.append(filteredPods[index])
			index = (index + 1) % len(filteredPods)
		
		return client.V1PodList(items=realPods), None


	# DeleteHelperPodBasedOnJobCleanupPolicy deletes specific helper pod based on jobCleanupPolicy
	def DeleteHelperPodBasedOnJobCleanupPolicy(self, podName, podLabel, chaosDetails):

		if chaosDetails.JobCleanupPolicy == "delete":
			logging.info("[Cleanup]: Deleting %s helper pod",(podName))
			err = self.DeletePod(podName, podLabel, chaosDetails.ChaosNamespace, chaosDetails.Timeout, chaosDetails.Delay)
			if err != None:
				logging.error("Unable to delete the helper pod, err: %s", err)

	# DeleteAllHelperPodBasedOnJobCleanupPolicy delete all the helper pods w/ matching label based on jobCleanupPolicy
	def DeleteAllHelperPodBasedOnJobCleanupPolicy(self, podLabel, chaosDetails):

		if chaosDetails.JobCleanupPolicy == "delete":
			logging.Info("[Cleanup]: Deleting all the helper pods")
			err = self.DeleteAllPod(podLabel, chaosDetails.ChaosNamespace, chaosDetails.Timeout, chaosDetails.Delay)
			if err != None :
				logging.info("Unable to delete the helper pods, err: %s", err)

	# GetServiceAccount derive the serviceAccountName for the helper pod
	def GetServiceAccount(self, chaosNamespace, chaosPodName, clients):
		
		try:
			pod = clients.clientk8s.read_namespaced_pod(chaosPodName, chaosNamespace)
		except Exception as e:
			return "", e
		
		return pod.spec.serviceAccountName, None


	#GetTargetContainer will fetch the container name from application pod
	#This container will be used as target container
	def GetTargetContainer(self, appNamespace, appName, clients):
		
		try:
			pod = clients.clientk8s.read_namespaced_pod(appName, appNamespace)
		except Exception as e:
			return "", e
		
		return pod.spec.containers[0].name, None


	#GetContainerID  derive the container id of the application container
	def GetContainerID(self, appNamespace, targetPod, targetContainer, clients):
		
		try:
			pod = clients.clientk8s.read_namespaced_pod(targetPod, appNamespace)
		except Exception as e:
			return e
		
		containerID = ''
		
		# filtering out the container id from the details of containers inside containerStatuses of the given pod
		# container id is present in the form of <runtime>:#<container-id>
		for container in pod.status.container_statuses:
			if container.name == targetContainer:
				containerID = container.ContainerID.split("//")[1]
				break

		logging.info("container ID of %s container, containerID: %s",(targetContainer, containerID))
		return containerID, None
	

	# CheckContainerStatus checks the status of the application container
	def CheckContainerStatus(self, appNamespace, appName, clients):
		
		try:
			try:
				pod = clients.clientk8s.read_namespaced_pod(appName, appNamespace)
			except Exception as e:
				return logging.error("Unable to find the pod with name :", appName), e
		
			for container in pod.status.containerStatuses:
				if container.Ready == False:
					return logging.info("Containers are not yet in running state")
				logging.InfoWithValues("The running status of container are as follows container : %s Pod : %s Status : %s", container.Name, pod.Name, pod.Status.Phase)
			return None
		except Exception as e:
			return e
