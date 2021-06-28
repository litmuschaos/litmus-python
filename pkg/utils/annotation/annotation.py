
import logging

# getDeploymentName derive the deployment name belongs to the given target pod
# it extract the parent name from the owner references
def getDeploymentName(targetPod,chaosDetails, clients):
	rsOwnerRef = targetPod.metadata.owner_references
	for own in rsOwnerRef :
		if own.kind == "ReplicaSet" :
			try:
				rs = clients.clientApps.read_namespaced_replica_set(own.name, chaosDetails.AppDetail.Namespace)
			except Exception as exp:
				return "", exp
			ownerRef = rs.metadata.owner_references
			for own in ownerRef:
				if own.kind == "Deployment":
					return own.name, None

	return "", ValueError("no deployment found for {} pod".format(targetPod.Name))


# getStatefulsetName derive the statefulset name belongs to the given target pod
# it extract the parent name from the owner references
def getStatefulsetName(targetPod,chaosDetails, clients):
	

	ownerRef = targetPod.metadata.owner_references
	for own in ownerRef:
		if own.kind == "StatefulSet":
			return own.name, None

	return "", ValueError("no statefulset found for {} pod".format(targetPod.Name))

# getDaemonsetName derive the daemonset name belongs to the given target pod
# it extract the parent name from the owner references
def getDaemonsetName(targetPod, chaosDetails, clients):
	
	ownerRef = targetPod.metadata.owner_references
	for own in ownerRef:
		if own.kind == "DaemonSet":
			return own.name, None

	return "", ValueError("no daemonset found for {} pod".format(targetPod.Name))

# getDeploymentConfigName derive the deploymentConfig name belongs to the given target pod
# it extract the parent name from the owner references
def getDeploymentConfigName(targetPod, chaosDetails, clients):

	rcOwnerRef = targetPod.metadata.owner_references
	for own in range(rcOwnerRef):
		if own.kind == "ReplicationController":
			try:
				rc = clients.clientCoreV1.read_namespaced_replication_controller(own.name, chaosDetails.AppDetail.Namespace)
			except Exception as exp:
				return "", exp
			
			ownerRef = rc.metadata.owner_references
			for own in ownerRef:
				if own.kind == "DeploymentConfig":
					return own.name, None
	return "", ValueError("No deploymentConfig found for {} pod".format(targetPod.Name))

# getDeploymentConfigName derive the rollout name belongs to the given target pod
# it extract the parent name from the owner references
def getRolloutName(targetPod, chaosDetails, clients):
	
	rsOwnerRef = targetPod.metadata.owner_references
	for own in rsOwnerRef :
		if own.kind == "ReplicaSet":
			try:
				rs = clients.clientsAppsV1.read_namespaced_replica_set(own.name, chaosDetails.AppDetail.Namespace)
			except Exception as exp:
				return "", exp
			
			ownerRef = rs.metadata.owner_references
			for own in ownerRef:
				if own.kind == "Rollout":
					return own.name, None
	return "", ValueError("no rollout found for {} pod".format(targetPod.Name))

# GetParentName derive the parent name of the given target pod
def GetParentName(clients, targetPod, chaosDetails):
	
	kind = chaosDetails.AppDetail.Kind
	if kind == "deployment" or kind == "deployments":
		return getDeploymentName(targetPod,chaosDetails, clients)
	elif kind == "statefulset" or kind == "statefulsets": 
		return getStatefulsetName(targetPod,chaosDetails, clients)
	elif kind == "daemonset" or kind == "daemonsets": 
		return getDaemonsetName(targetPod,chaosDetails, clients)
	elif kind == "deploymentConfig" or kind == "deploymentConfigs": 
		return getDeploymentConfigName(targetPod,chaosDetails, clients)
	elif kind == "rollout" or kind == "rollouts": 
		return getRolloutName(targetPod,chaosDetails, clients)
	else:
		return False,  ValueError("Appkind: {} is not supported".format(kind))
	
# IsParentAnnotated check whether the target pod's parent is annotated or not
def IsParentAnnotated(clients, parentName, chaosDetails):
	if chaosDetails.AppDetail.Kind.lower() == "deployment" or chaosDetails.AppDetail.Kind.lower() == "deployments":
		try:
			deploy = clients.clientApps.read_namespaced_deployment(name=parentName, namespace=chaosDetails.AppDetail.Namespace)
		except Exception as exp:
			return False, exp
		if deploy.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) == chaosDetails.AppDetail.AnnotationValue:
			return True, None

	elif chaosDetails.AppDetail.Kind.lower() =="statefulset" or  chaosDetails.AppDetail.Kind.lower() == "statefulsets":
		try:
			sts = clients.clientApps.read_namespaced_stateful_set(name=parentName, namespace=chaosDetails.AppDetail.Namespace)
		except Exception as exp:
			return False, exp
	
		if sts.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) == chaosDetails.AppDetail.AnnotationValue:
			return True, None

	elif chaosDetails.AppDetail.Kind.lower() =="daemonset" or  chaosDetails.AppDetail.Kind.lower() == "daemonsets":
		try:
			ds = clients.clientApps.read_namespaced_daemon_set(name=parentName, namespace=chaosDetails.AppDetail.Namespace)
		except Exception as exp:
			return False, exp

		if ds.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) == chaosDetails.AppDetail.AnnotationValue:
			return True, None

	elif chaosDetails.AppDetail.Kind.lower() == "deploymentconfig":
		try:
			dc = clients.clientDyn.resources.get(api_version="v1", kind="DeploymentConfig", group="apps.openshift.io").get(namespace=chaosDetails.AppDetail.Namespace, name=parentName)
		except Exception as exp:
			return False, exp

		if dc.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) == chaosDetails.AppDetail.AnnotationValue:
			return True, None

	elif chaosDetails.AppDetail.Kind.lower() == "rollout":
		try:
			ro = clients.clientDyn.resources.get(api_version="v1alpha1", kind="Rollout", group="argoproj.io").get(namespace=chaosDetails.AppDetail.Namespace, name=parentName)
		except Exception as exp:
			return "", exp
	
		if ro.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) == chaosDetails.AppDetail.AnnotationValue:
			return True, None

	else:
		return False, ValueError("{} appkind is not supported".format(chaosDetails.AppDetail.Kind))

	return False, None
