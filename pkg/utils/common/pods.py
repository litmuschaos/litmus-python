from kubernetes import client, config
import time
from pkg.types.types import ChaosDetails
import logging
from retry import retry
import logging
from pkg.utils.annotation.annotation import IsPodParentAnnotated
logger = logging.getLogger(__name__)
from chaosk8s import create_k8s_api_client
from chaoslib.types import MicroservicesStatus, Secrets
# AUTStatusCheck checks the status of application under test
# if annotationCheck is True, it will check the status of the annotated pod only
# else it will check status of all pods with matching label
class Application(object):
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
	
	def DeletePodRetry(self):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		try:
			podSpec = v1.list_namespaced_pod(self.namespace, label_selector=self.podLabel)
			if len(podSpec.items) == 0:
				logging.Errorf("no pods found with matching labels") 
		except:
			logging.Errorf("no pods found with matching labels")
		return None
	
	def DeleteAllPodRetry(self):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		try:
			podSpec = v1.list_namespaced_pod(self.namespace, label_selector=self.podLabel)
			if len(podSpec.items) == 0:
				logging.Errorf("no pods found with matching labels") 
		except:
			logging.Errorf("no pods found with matching labels")
		return None
	
	#DeletePod deletes the specified pod and wait until it got terminated
	def DeletePod(self):

		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		try:
			v1.delete_namespaced_pod(self.podName, self.namespace)
		except Exception as e:
			return False,logger.Errorf("no pod found with matching label, err: %v", e)
		# waiting for the termination of the pod
		return self.DeletePodRetry()
	

	#DeleteAllPod deletes all the pods with matching labels and wait until all the pods got terminated
	def DeleteAllPod(self):

		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		try:
			v1.delete_collection_namespaced_pod(self.namespace, label_selector=self.podLabel)
		except Exception as e:
			return False,logger.Errorf("no pod found with matching label, err: %v", e)
		# waiting for the termination of the pod
		return self.DeleteAllPodRetry()

	# GetChaosPodAnnotation will return the annotation on chaos pod
	def GetChaosPodAnnotation(self):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(self.podName, self.namespace)
		except Exception as e:
			return e
		return pod.metadata.annotations, None
	

	# GetImagePullSecrets return the imagePullSecrets from the experiment pod
	def GetImagePullSecrets(self):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(self.podName, self.namespace)
		except Exception as e:
			return e
		return pod.Spec.ImagePullSecrets, None
	

	# GetChaosPodResourceRequirements will return the resource requirements on chaos pod
	def GetChaosPodResourceRequirements(self):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(self.podName, self.namespace)
		except Exception as e:
			return e, e 
		#if err != None :
		#	return core_v1.ResourceRequirements{}, err
		
		for  container in pod.spec.containers:
			# The name of chaos container is always same as job name
			# <experiment-name>-<runid>
			if container.name == self.containerName:
				return container.resources, None
		
		return None, logger.Errorf("No container found with %v name in target pod", self.containerName)
	

	# VerifyExistanceOfPods check the availibility of list of pods
	def VerifyExistanceOfPods(self):

		if self.pods == "":
			return False, None
		podList = self.pods.split(",")
		for index in podList:
			isPodsAvailable, err = self.CheckForAvailibiltyOfPod(self.namespace, podList[index], self.clients)
			if err != None :
				return False, err			
			if isPodsAvailable == False:
				return isPodsAvailable, None

		return True, None
	

	#GetPodList check for the availibilty of the target pod for the chaos execution
	# if the target pod is not defined it will derive the random target pod list using pod affected percentage
	def GetPodList(self):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		try:
			podList = v1.list_namespaced_pod(self.chaosDetails.AppDetail.Namespace, label_selector=self.chaosDetails.AppDetail.Label)
		except Exception as e:
			return e
		if len(podList.Items) == 0:
    			return False,logger.Wrapf("Failed to find the pod with matching labels in {} namespace", self.chaosDetails.AppDetail.Namespace)
		
		isPodsAvailable, err = self.VerifyExistanceOfPods(self.chaosDetails.AppDetail.Namespace, self.targetPods, self.clients)
		if err != None:
			return False, err
		
		# getting the pod, if the target pods is defined
		# else select a random target pod from the specified labels
		if isPodsAvailable == True:
			podList, err = self.GetTargetPodsWhenTargetPodsENVSet(self.targetPods, self.clients, self.chaosDetails)
			if err != None:
				return False, err
			
			#realpods.Items = append(realpods.Items, podList.Items...)
		else:
			nonChaosPods = self.FilterNonChaosPods(podList, self.chaosDetails)
			realpods, err = self.GetTargetPodsWhenTargetPodsENVNotSet(self.podAffPerc, self.clients, self.nonChaosPods, self.chaosDetails)
			if err != None:
				return core_v1.PodList, err
		logger.infof("[Chaos]:Number of pods targeted: %v", len(realpods.Items))
		return realpods, None
	

	# CheckForAvailibiltyOfPod check the availibility of the specified pod
	def CheckForAvailibiltyOfPod(self): 
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		if name == "" :
			return False, None
		try:
			pod = v1.read_namespaced_pod(self.name, self.namespace)
		except Exception as e:
			return False, e 
		
		if k8serrors ==  False:
			return False, err
		#elif err != None & k8serrors.IsNotFound(err):
		#	return False, None
		
		return True, None
	

	#FilterNonChaosPods remove the chaos pods(operator, runner) for the podList
	# it filter when the applabels are not defined and it will select random pods from appns
	def FilterNonChaosPods(self):
		if self.chaosDetails.AppDetail.Label == "":
			nonChaosPods = {}
			# ignore chaos pods
			for index, pod in self.podList.items:
				if (pod.Labels["chaosUID"] != (self.chaosDetails.ChaosUID) or pod.Labels["name"] == "chaos-operator"):
					nonChaosPods = nonChaosPods.update(self.podList.Items[index])
					
			return nonChaosPods
		return self.podList
	

	# GetTargetPodsWhenTargetPodsENVSet derive the specific target pods, if TARGET_PODS env is set
	def GetTargetPodsWhenTargetPodsENVSet(self):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			podList = v1.list_namespaced_pod(self.chaosDetails.AppDetail.Namespace, label_selector=self.chaosDetails.AppDetail.Label)
		except Exception as e:
			return {}, e
		
		if len(podList.items) == 0 :
			return {},logger.error("Failed to find the pods with matching labels in {} namespace", self.chaosDetails.AppDetail.Namespace)


		targetPodsList = self.targetPods.split(",")
		realPods = {}

		for pod in podList.items :
			for index in targetPodsList :
				if targetPodsList[index] == pod.name :
					if self.chaosDetails.AppDetail.AnnotationCheck == True:
						isPodAnnotated, err = IsPodParentAnnotated(self.clients, pod, self.chaosDetails)
						if err != None :
							return {}, err
						
						if isPodAnnotated == False:
							return {},logger.Errorf("%v target pods are not annotated", self.targetPods)


					realPods = realPods.update(pod)

		
		return realPods, None
	

	# GetTargetPodsWhenTargetPodsENVNotSet derives the random target pod list, if TARGET_PODS env is not set
	def GetTargetPodsWhenTargetPodsENVNotSet(self):
		filteredPods = {}
		realPods = {}

		if self.chaosDetails.AppDetail.AnnotationCheck == True:
			for _, pod in self.nonChaosPods.items:
				isPodAnnotated, err = IsPodParentAnnotated(self.clients, pod, self.chaosDetails)
				if err != None:
					return {}, err
				
				if isPodAnnotated == True:
					filteredPods.Items = filteredPods.update(pod)
				
			
			if len(filteredPods) == 0:
				return filteredPods,logger.Errorf("No annotated target pod found")
			
		else:
			filteredPods = nonChaosPods
		

		newPodListLength = math.Maximum(1, math.Adjustment(self.podAffPerc, len(filteredPods)))
		rand.Seed(time.Now().UnixNano())

		# it will generate the random podlist
		# it starts from the random index and choose requirement no of pods next to that index in a circular way.
		index = rand.Intn(len(filteredPods.Items))
		for i in newPodListLength:
			realPods = realPods.update(filteredPods.Items[index])
			index = (index + 1) % len(filteredPods.Items)
		
		return realPods, None


	# DeleteHelperPodBasedOnJobCleanupPolicy deletes specific helper pod based on jobCleanupPolicy
	def DeleteHelperPodBasedOnJobCleanupPolicy(self):

		if self.chaosDetails.JobCleanupPolicy == "delete":
			logger.Infof("[Cleanup]: Deleting %v helper pod", self.podName)
			err = self.DeletePod(self.podName, self.podLabel, self.chaosDetails.ChaosNamespace, self.chaosDetails.Timeout, self.chaosDetails.Delay, self.clients)
			if err != None:
				logger.Errorf("Unable to delete the helper pod, err: %v", err)
			
		
	

	# DeleteAllHelperPodBasedOnJobCleanupPolicy delete all the helper pods w/ matching label based on jobCleanupPolicy
	def DeleteAllHelperPodBasedOnJobCleanupPolicy(self):

		if self.chaosDetails.JobCleanupPolicy == "delete":
			logger.Info("[Cleanup]: Deleting all the helper pods")
			err = self.DeleteAllPod(self.podLabel, self.chaosDetails.ChaosNamespace, self.chaosDetails.Timeout, self.chaosDetails.Delay, self.clients)
			if err != None :
				logger.Errorf("Unable to delete the helper pods, err: %v", err)




	# GetServiceAccount derive the serviceAccountName for the helper pod
	def GetServiceAccount(self):
		api = create_k8s_api_client(secrets = None)
		v1 = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(self.targetPod, self.namespace)
		except Exception as e:
			return "", e
		
		return pod.Spec.ServiceAccountName, None


	#GetTargetContainer will fetch the container name from application pod
	#This container will be used as target container
	def GetTargetContainer(self):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(self.appName, self.appNamespace)
		except Exception as e:
			return "", e
		
		return pod.spec.containers[0].name, None


	#GetContainerID  derive the container id of the application container
	def GetContainerID(self):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		
		try:
			pod = v1.read_namespaced_pod(self.targetPod, self.appNamespace)
		except Exception as e:
			return e
		
		containerID = ''
		
		# filtering out the container id from the details of containers inside containerStatuses of the given pod
		# container id is present in the form of <runtime>:#<container-id>
		for container in pod.Status.ContainerStatuses:
			if container.name == self.targetContainer:
				containerID = container.ContainerID.split("//")[1]
				break

		logger.Infof("container ID of %v container, containerID: %v", self.targetContainer, containerID)
		return containerID, None
	

	# CheckContainerStatus checks the status of the application container
	def CheckContainerStatus(self):
		api = create_k8s_api_client(secrets=None)
		v1  = client.CoreV1Api(api)
		
		try:
			try:
				pod = v1.read_namespaced_pod(self.appName, self.appNamespace)
			except Exception as e:
				return logger.Errorf("unable to find the pod with name :", self.appName), e
		
			for container in pod.status.containerStatuses:
				if container.Ready == False:
					return logger.Errorf("containers are not yet in running state")
				logger.InfoWithValues("The running status of container are as follows",
					"container :", container.Name, "Pod :", pod.Name, "Status :", pod.Status.Phase)
			return None
		except Exception as e:
			return e
