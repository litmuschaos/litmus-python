
import logging

# getDeploymentName derive the deployment name belongs to the given target pod
# it extract the parent name from the owner references
def getDeploymentName(targetPod,chaosDetails, clients):
	deployList = clients.clientApps.list_namespaced_deployment(namespace=chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	if len(deployList.items) == 0:
		return False, ValueError("No deployment found with matching label")
	rsOwnerRef = targetPod.metadata.owner_references
	for deploy in deployList.items:
		for own in rsOwnerRef :
			if own.kind == "ReplicaSet" :
				try:
					rs = clients.clientApps.read_namespaced_replica_set(own.name, chaosDetails.AppDetail.Namespace)
				except Exception as exp:
					return "", exp
				ownerRef = rs.metadata.owner_references
				for own in ownerRef:
					if own.kind == "Deployment" and own.name == deploy.metadata.name:
						return deploy.metadata.name, None
	
	return "", ValueError("no deployment found for {} pod".format(targetPod.Name))


# getStatefulsetName derive the statefulset name belongs to the given target pod
# it extract the parent name from the owner references
def getStatefulsetName(targetPod,chaosDetails, clients):
	
	stsList = clients.clientApps.list_namespaced_stateful_set(namespace=chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	if len(stsList.items) == 0:
		return "", ValueError("No statefulset found with matching label")

	for sts in stsList.items:
		ownerRef = targetPod.metadata.owner_references
		for own in ownerRef:
			if own.kind == "StatefulSet" and own.name == sts.metadata.name:
				return sts.metadata.name, None

	return "", ValueError("no statefulset found for {} pod".format(targetPod.Name))

# getDaemonsetName derive the daemonset name belongs to the given target pod
# it extract the parent name from the owner references
def getDaemonsetName(targetPod, chaosDetails, clients):
	
	dsList = clients.clientApps.list_namespaced_daemon_set(namespace=chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	if len(dsList.items) == 0:
		return "", ValueError("No daemonset found with matching label")
	
	for ds in dsList.items:
		ownerRef = targetPod.metadata.owner_references
		for own in ownerRef:
			if own.kind == "DaemonSet" and own.name == ds.metadata.name:
				logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",chaosDetails.AppDetail.Kind, ds.metadata.name, ds.metadata.namespace)
				return ds.metadata.name, None

	return "", ValueError("no daemonset found for {} pod".format(targetPod.Name))

# getDeploymentConfigName derive the deploymentConfig name belongs to the given target pod
# it extract the parent name from the owner references
def getDeploymentConfigName(targetPod, chaosDetails, clients):

	try:
		deploymentConfigList = clients.clientDyn.resources.get(api_version="v1", kind="DeploymentConfig", group="apps.openshift.io").get(namespace=chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	except Exception as exp:
		return "", exp
	if len(deploymentConfigList.items) == 0:
		return "", ValueError("No deploymentconfig found with matching labels")
	
	for dc in deploymentConfigList.items:
		rcOwnerRef = targetPod.metadata.owner_references
		for own in range(rcOwnerRef):
			if own.kind == "ReplicationController":
				try:
					rc = clients.clientCoreV1.read_namespaced_replication_controller(own.name, chaosDetails.AppDetail.Namespace)
				except Exception as exp:
					return "", exp
				
				ownerRef = rc.metadata.owner_references
				for own in ownerRef:
					if own.kind == "DeploymentConfig" and own.name == dc.metadata.name:
						return dc.metadata.name, None
	return "", ValueError("No deploymentConfig found for {} pod".format(targetPod.Name))

# getDeploymentConfigName derive the rollout name belongs to the given target pod
# it extract the parent name from the owner references
def getRolloutName(targetPod, chaosDetails, clients):
	
	try:
		rolloutList = clients.clientDyn.resources.get(api_version="v1alpha1", kind="Rollout", group="argoproj.io").get(namespace=chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	except Exception as exp:
		return "", exp
	if len(rolloutList.items) == 0:
		return "", ValueError("No rolloutList found with matching labels")
	for ro in rolloutList.items :
		rsOwnerRef = targetPod.metadata.owner_references
		for own in rsOwnerRef :
			if own.kind == "ReplicaSet":
				try:
					rs = clients.clientsAppsV1.read_namespaced_replica_set(own.name, chaosDetails.AppDetail.Namespace)
				except Exception as exp:
					return "", exp
				
				ownerRef = rs.metadata.owner_references
				for own in ownerRef:
					if own.kind == "Rollout" and own.name == ro.metadata.name:
						return ro.metadata.name, None
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
		if str(deploy.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			return True, None

	elif chaosDetails.AppDetail.Kind.lower() =="statefulset" or  chaosDetails.AppDetail.Kind.lower() == "statefulsets":
		try:
			sts = clients.clientApps.read_namespaced_stateful_set(name=parentName, namespace=chaosDetails.AppDetail.Namespace)
		except Exception as exp:
			return False, exp
	
		if str(sts.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			return True, None

	elif chaosDetails.AppDetail.Kind.lower() =="daemonset" or  chaosDetails.AppDetail.Kind.lower() == "daemonsets":
		try:
			ds = clients.clientApps.read_namespaced_daemon_set(name=parentName, namespace=chaosDetails.AppDetail.Namespace)
		except Exception as exp:
			return False, exp

		if str(ds.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			return True, None

	elif chaosDetails.AppDetail.Kind.lower() == "deploymentconfig":
		try:
			dc = clients.clientDyn.resources.get(api_version="v1", kind="DeploymentConfig", group="apps.openshift.io").get(namespace=chaosDetails.AppDetail.Namespace, name=parentName)
		except Exception as exp:
			return False, exp

		if str(dc.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			return True, None

	elif chaosDetails.AppDetail.Kind.lower() == "rollout":
		try:
			ro = clients.clientDyn.resources.get(api_version="v1alpha1", kind="Rollout", group="argoproj.io").get(namespace=chaosDetails.AppDetail.Namespace, name=parentName)
		except Exception as exp:
			return "", exp
	
		if str(ro.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			return True, None

	else:
		return False, ValueError("{} appkind is not supported".format(chaosDetails.AppDetail.Kind))

	return False, None
