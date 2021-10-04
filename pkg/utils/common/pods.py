from kubernetes import client
import random
import logging
import pkg.utils.annotation.annotation as annotation
import pkg.utils.k8serror.k8serror as k8serror
import pkg.maths.maths as maths

# Pods class is to set, delete, retreive, verify etc... activity for pods and containers 
class Pods(object):

	# GetChaosPodAnnotation will return the annotation on chaos pod
	def GetChaosPodAnnotation(self, clients, podName, namespace):
		
		try:
			pod = clients.clientCoreV1.read_namespaced_pod(podName, namespace)
		except Exception as exp:
			return None, exp
		return pod.metadata.annotations, None
	
	# VerifyExistanceOfPods check the availibility of list of pods
	def VerifyExistanceOfPods(self, namespace, pods, clients):

		if pods == "":
			return False, None
		podList = pods.split(",")
		for pod in podList:
			isPodsAvailable, err = self.CheckForAvailibiltyOfPod(namespace, pod, clients)
			if err != None :
				return False, err			
			if not isPodsAvailable:
				return isPodsAvailable, ValueError("{} pod is not available in {} namespace".format(pod, namespace))

		return True, None

	#GetPodList check for the availibilty of the target pod for the chaos execution
	# if the target pod is not defined it will derive the random target pod list using pod affected percentage
	def GetPodList(self, targetPods, podAffPerc , chaosDetails, clients):
		
		realpods = client.V1PodList
		isPodsAvailable, err = self.VerifyExistanceOfPods(chaosDetails.AppDetail.Namespace, targetPods, clients)
		if err != None:
			return client.V1PodList, err

		# getting the pod, if the target pods is defined
		# else select a random target pod from the specified labels
		if isPodsAvailable:
			realpods, err = self.GetTargetPodsWhenTargetPodsENVSet(targetPods, chaosDetails, clients)
			if err != None or len(realpods.items) == 0:
				return client.V1PodList, err
		else:
			nonChaosPods = self.FilterNonChaosPods(chaosDetails, clients)
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
			clients.clientCoreV1.read_namespaced_pod(name, namespace)
		except Exception as err:
			if k8serror.K8serror().IsNotFound(err):
				return False, None
			else:
				return False, err

		return True, None
	
	#FilterNonChaosPods remove the chaos pods(operator, runner) for the podList
	# it filter when the applabels are not defined and it will select random pods from appns
	def FilterNonChaosPods(self, chaosDetails, clients):
		try:
			podList = clients.clientCoreV1.list_namespaced_pod(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
		except Exception as exp:
			return client.V1PodList, exp
		if len(podList.items) == 0:
				return False, ValueError("Failed to find the pod with matching labels in {} namespace".format(chaosDetails.AppDetail.Namespace))

		nonChaosPods = []
		# ignore chaos pods
		for pod in podList.items:
			if pod.metadata.labels.get("chaosUID") == None and pod.metadata.labels.get("name") != "chaos-operator": 
				nonChaosPods.append(pod)
		return client.V1PodList(items=nonChaosPods)

	# GetTargetPodsWhenTargetPodsENVSet derive the specific target pods, if TARGET_PODS env is set
	def GetTargetPodsWhenTargetPodsENVSet(self, targetPods, chaosDetails, clients):

		targetPodsList = targetPods.split(",")
		realPodList = []
		
		for targetPod in targetPodsList :
			try:
				pod = clients.clientCoreV1.read_namespaced_pod(targetPod, chaosDetails.AppDetail.Namespace)
			except Exception as exp:
				return client.V1PodList, exp

			if chaosDetails.AppDetail.AnnotationCheck:
				parentName, err = annotation.GetParentName(clients, pod, chaosDetails)
				if err != None:
					return client.V1PodList, err
				
				isPodAnnotated, err = annotation.IsParentAnnotated(clients, parentName, chaosDetails)
				if err != None :
					return client.V1PodList, err
				
				if not isPodAnnotated:
					return client.V1PodList, ValueError("{} target pods are not annotated".format(targetPods))

			realPodList.append(pod)

		return client.V1PodList(items=realPodList), None
	
	# GetTargetPodsWhenTargetPodsENVNotSet derives the random target pod list, if TARGET_PODS env is not set
	def GetTargetPodsWhenTargetPodsENVNotSet(self, podAffPerc , nonChaosPods, chaosDetails, clients):
		
		filteredPods = []
		realPods = []
		for pod in nonChaosPods.items:
			if chaosDetails.AppDetail.AnnotationCheck:
				parentName, err = annotation.GetParentName(clients, pod, chaosDetails)
				if err != None:
					return client.V1PodList, err
				isParentAnnotated, err = annotation.IsParentAnnotated(clients, parentName, chaosDetails)
				if err != None:
					return client.V1PodList, err 	
				
				if isParentAnnotated:
					filteredPods.append(pod)
			else:
				filteredPods.append(pod)

		if len(filteredPods) == 0:
			return client.V1PodList(items=filteredPods), ValueError("No target pod found")
			
		newPodListLength = max(1, maths.Adjustment(min(podAffPerc,100), len(filteredPods)))
		
  		# it will generate the random podlist
		# it starts from the random index and choose requirement no of pods next to that index in a circular way.
		index = random.randint(0,len(filteredPods)-1)
		for i in range(int(newPodListLength)):
			realPods.append(filteredPods[index])
			index = (index + 1) % len(filteredPods)
		
		return client.V1PodList(items=realPods), None
