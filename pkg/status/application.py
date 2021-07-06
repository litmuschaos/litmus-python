import time
import logging
import pkg.utils.annotation.annotation as annotation

# Application class is checking the status of application
class Application(object):
	
	# AUTStatusCheck checks the status of application under test
	# if annotationCheck is true, it will check the status of the annotated pod only
	# else it will check status of all pods with matching label
	def AUTStatusCheck(self, appNs, appLabel, containerName, timeout, delay, chaosDetails, clients):
		
		if chaosDetails.AppDetail.AnnotationCheck:
			logging.info("[Info]: Check Annotated for Applications Status")
			err = self.AnnotatedApplicationsStatusCheck(clients, appNs, appLabel, containerName, chaosDetails, 0, timeout, delay)
			if err != None:
				return err
		else:
			if appLabel == "" :
				# Checking whether applications are healthy
				logging.info("[status]: No appLabels provided, skipping the application status checks")
			else:
				# Checking whether application containers are in ready state
				logging.info("[status]: Checking whether application containers are in ready state")
				err = self.CheckContainerStatus(clients, appNs, appLabel, containerName, 0, timeout, delay)
				if err != None:
					return err
				
				# Checking whether application pods are in running state
				logging.info("[status]: Checking whether application pods are in running state")
				err = self.CheckPodStatus(clients, appNs, appLabel, 0, timeout, delay)
				if err != None:
					return err
		return None
	
	#AnnotatedApplicationsStatusCheck checks the status of all the annotated applications with matching label
	def AnnotatedApplicationsStatusCheck(self, clients, appNs, appLabel, containerName, chaosDetails, init, timeout, delay):
		
		try:
			podList = clients.clientCoreV1.list_namespaced_pod(appNs, label_selector=appLabel)
			if len(podList.items) == 0:
				raise Exception("Unable to find the pods with matching labels")
			for pod in podList.items:
				
				parentName, err = annotation.GetParentName(clients, pod, chaosDetails)
				if err != None:
					return err
				
				
				isParentAnnotated, err = annotation.IsParentAnnotated(clients, parentName, chaosDetails)
				if err != None:
					raise Exception("Unable to find the pods with Annotation :{}".format(chaosDetails.AppDetail.AnnotationValue))
				
				if isParentAnnotated:
					if containerName == "":
				
						for  container in pod.status.container_statuses:
							if container.state.terminated != None: 
								raise Exception("Container is in terminated state")
				
							if not container.ready:
								raise Exception("containers are not yet in running state")
							
							logging.info("[status]: The Container status are as follows Container : %s, Pod : %s, Readiness : %s", container.name, pod.metadata.name, container.ready)
						
					else:
						
						for container in pod.status.container_statuses:
							if containerName == container.name:
								if container.state.terminated != None:
									raise Exception("container is in terminated state")
								
								if not container.ready:
									raise Exception("containers are not yet in running state")
								
								logging.info("[status]: The Container status are as follows Container : %s, Pod : %s, Readiness : %s.", container.name, pod.metadata.name, container.ready)
					if pod.status.phase != "Running":
						raise Exception("{} pod is not yet in running state".format(pod.metadata.name))
		
					logging.info("[status]: The status of Pods are as follows Pod : %s, status : %s.", pod.metadata.name, pod.status.phase)
		except Exception as exp:
			if init > timeout:
				return exp
			time.sleep(delay)
			return self.AnnotatedApplicationsStatusCheck(clients,appNs, appLabel, containerName, chaosDetails, init + delay, timeout, delay)
		
		return None

	# CheckApplicationStatus checks the status of the AUT
	def CheckApplicationStatus(self, appNs, appLabel, timeout, delay, clients):

		if appLabel == "":
			# Checking whether applications are healthy
			logging.info("[status]: No appLabels provided, skipping the application status checks")
		else:
			# Checking whether application containers are in ready state
			logging.info("[status]: Checking whether application containers are in ready state")
			err = self.CheckContainerStatus(clients,appNs, appLabel, "", 0, timeout, delay)
			if err != None:
				return err
			
			# Checking whether application pods are in running state
			logging.info("[status]: Checking whether application pods are in running state")
			err = self.CheckPodStatus(clients, appNs, appLabel, 0, timeout, delay); 
			if err != None:
				return err

		return None
	
	# CheckAuxiliaryApplicationStatus checks the status of the Auxiliary applications
	def CheckAuxiliaryApplicationStatus(self, AuxiliaryAppDetails, timeout, delay):

		AuxiliaryAppInfo = AuxiliaryAppDetails.split(",")
		for val in AuxiliaryAppInfo:
			AppInfo = val.split(":")
			err = self.CheckApplicationStatus(AppInfo[0], AppInfo[1])
			if err != None:
				return err

		return None
	
	# CheckPodStatusPhase is helper to checks the running status of the application pod
	def CheckPodStatusPhase(self,clients, appNs, appLabel, states, init, timeout, delay):
			
		try:
			podList = clients.clientCoreV1.list_namespaced_pod(appNs, label_selector=appLabel)
			if len(podList.items) == 0:
				return Exception("Unable to find the pods with matching labels, err: {}".format(appLabel))
			for pod in podList.items:
				if str(pod.status.phase) != states: 
					raise Exception("Pod is not yet in %s state(s)",(states))
			
				logging.info("[status]: The status of Pods are as follows Pod : %s status : %s", pod.metadata.name, pod.status.phase)
		except Exception as exp:
			if init > timeout:
				return ValueError(exp)
			time.sleep(delay)		
			return self.CheckPodStatusPhase(clients, appNs,appLabel, states, init + delay, timeout, delay)
				
		return None

	# CheckPodStatus checks the running status of the application pod
	def CheckPodStatus(self, clients, appNs, appLabel, tries, timeout, delay):
		return self.CheckPodStatusPhase(clients, appNs, appLabel, "Running", tries, timeout, delay)
	
	#CheckContainerStatus checks the status of the application container for given timeout, if it does not match label it will 
	def CheckContainerStatus(self, clients, appNs, appLabel, containerName, init, timeout, delay):
		
		try:
			podList = clients.clientCoreV1.list_namespaced_pod(appNs, label_selector=appLabel)
			if len(podList.items) == 0:
				raise Exception("Unable to find the pods with matching labels")
			
			for pod in podList.items:
				if containerName == "":
				
					err = self.validateAllContainerStatus(pod.metadata.name, pod.status.container_statuses, clients)
					if err != None:
						raise Exception(err)
				else:
					err = self.validateContainerStatus(containerName, pod.metadata.name, pod.status.container_statuses, clients); 
					if err != None:
						raise Exception(err)
		except Exception as exp:
			if init > timeout:
				return ValueError(exp)
			time.sleep(delay)
			return self.CheckContainerStatus(clients, appNs,appLabel,containerName, init + delay, timeout, delay)
				
		return None

	# validateContainerStatus verify that the provided container should be in ready state
	def validateContainerStatus(self, containerName, podName, ContainerStatuses, clients):
		for container in ContainerStatuses:
			if container.name == containerName:
				if container.state.terminated != None :
					return ValueError("container is in terminated state")
				if not container.ready:
					return ValueError("containers are not yet in running state")
				
				logging.info("[status]: The Container status are as follows Container : %s, Pod : %s, Readiness : %s", container.name, podName, container.ready)
		return None
	
	# validateAllContainerStatus verify that the all the containers should be in ready state
	def validateAllContainerStatus(self, podName, ContainerStatuses, clients):
		for container in ContainerStatuses:
			err = self.validateContainerStatus(container.name, podName, ContainerStatuses, clients)
			if err != None:
				return ValueError(err)
		return None

