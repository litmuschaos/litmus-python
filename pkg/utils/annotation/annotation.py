
from kubernetes import client, config, dynamic
from kubernetes.client.rest import ApiException
import logging
logging.basicConfig(format='time=%(asctime)s level=%(levelname)s  msg=%(message)s', level=logging.INFO)  
from kubernetes.client import api_client
import os

global conf
if os.getenv('KUBERNETES_SERVICE_HOST'):
	conf = config.load_incluster_config()
else:
	conf = config.load_kube_config()

def deployment(targetPod,chaosDetails):
	api_instance = client.AppsV1Api()
	try:
		deployList = api_instance.list_namespaced_deployment(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	except ApiException as e:
	 	return False, logging.error("no deployment found with matching label, err: %s",(e))
	for deploy in deployList.items:
		if str(deploy.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			rsOwnerRef = targetPod.metadata.owner_references
			for own in rsOwnerRef :
				if own.kind == "ReplicaSet" :
					try:
						rs = api_instance.read_namespaced_replica_set(own.name, chaosDetails.AppDetail.Namespace)
					except Exception as e:
						return False, e
					ownerRef = rs.metadata.owner_references
					for own in ownerRef:
						if own.kind == "Deployment" and own.name == deploy.metadata.name:
							logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",(chaosDetails.AppDetail.Kind, deploy.metadata.name, deploy.metadata.namespace))
							return True, None
	return False, False
def statefulset(targetPod,chaosDetails):
	v1 = client.AppsV1Api()
	
	try:
		stsList = v1.list_namespaced_stateful_set("litmus")
	except Exception as e:
		return False, e
	if len(stsList.items) == 0:
		return False, logging.error("no statefulset found with matching label")
	
	for sts in stsList.items:
		if str(sts.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			ownerRef = targetPod.metadata.owner_references
			for own in ownerRef:
				if own.kind == "StatefulSet" and own.name == sts.name:
					logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",(chaosDetails.AppDetail.Kind, sts.metadata.name, sts.metadata.namespace))
					return True, None

def daemonset(targetPod, chaosDetails):
	v1 = client.AppsV1Api()

	try:
		dsList = v1.list_namespaced_daemon_set(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	except Exception as e:
		return False, e
	if len(dsList.items) == 0:
		return False, logging.error("no daemonset found with matching label")
	
	for ds in dsList.items:
		if str(ds.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			ownerRef = targetPod.metadata.owner_references
			for own in ownerRef:
				if own.kind == "DaemonSet" and own.name == ds.name:
					logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",(chaosDetails.AppDetail.Kind, ds.metadata.name, ds.metadata.namespace))
					return True, None

def deploymentconfig(targetPod, chaosDetails):
	v1 = client.CoreV1Api()
	
	clientDyn = dynamic.DynamicClient(
        api_client.ApiClient(conf)
    )

	try:
		deploymentConfigList = clientDyn.resources.get(api_version="v1", kind="DeploymentConfig", group="apps.openshift.io", label_selector=chaosDetails.AppDetail.Label)
	except Exception as e:
		return False, e
	if None or len(deploymentConfigList.items) == 0:
		return False, logging.error("no deploymentconfig found with matching labels")
	
	for dc in deploymentConfigList.items:
		if str(dc.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			rcOwnerRef = targetPod.metadata.owner_references
			for own in range(rcOwnerRef):
				if own.kind == "ReplicationController":
					try:
						rc = v1.read_namespaced_replication_controller(own.name, chaosDetails.AppDetail.Namespace)
					except Exception as e:
						return False, e
					
					ownerRef = rc.metadata.owner_references
					for own in ownerRef:
						if own.kind == "DeploymentConfig" and own.name == dc.GetName():
							logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",(chaosDetails.AppDetail.Kind, dc.metadata.name, dc.metadata.namespace))
							return True, None

def rollout(targetPod, chaosDetails):
	v1 = client.AppsV1beta1Api()
	
	clientDyn = dynamic.DynamicClient(
        api_client.ApiClient(conf)
    )
	
	try:
		rolloutList = clientDyn.resources.get(api_version="v1alpha1", kind="Rollout", group="argoproj.io", label_selector=chaosDetails.AppDetail.Label)
	except Exception as e:
		return False, logging.error("no rollouts found with matching labels")
	
	for ro in rolloutList.items :
		if str(ro.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			rsOwnerRef = targetPod.metadata.owner_references
			for own in rsOwnerRef :
				if own.kind == "ReplicaSet":
					try:
						rs = v1.read_namespaced_replica_set(own.name, chaosDetails.AppDetail.Namespace)
					except Exception as e:
						return False, e
					
					ownerRef = rs.metadata.owner_references
					for own in ownerRef:
						if own.kind == "Rollout" and own.name == ro.metadata.name:
							logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",(chaosDetails.AppDetail.Kind, ro.metadata.name, ro.metadata.namespace))
							return True, None

# PodParentAnnotated is helper method to check whether the target pod's parent is annotated or not
def PodParentAnnotated(argument, targetPod,chaosDetails):
	if argument == "deployment":
		return deployment(targetPod,chaosDetails)
	elif argument == "statefulset": 
		return statefulset(targetPod,chaosDetails)
	elif argument == "daemonset": 
		return daemonset(targetPod,chaosDetails)
	elif argument == "deploymentConfig": 
		return deploymentconfig(targetPod,chaosDetails)
	elif argument == "rollout" : 
		return rollout(targetPod,chaosDetails)
	else:
		return False,  logging.info("Appkind: %s is not supported",(argument))
	
# IsPodParentAnnotated check whether the target pod's parent is annotated or not
def IsPodParentAnnotated(targetPod, chaosDetails):

    return PodParentAnnotated(chaosDetails.AppDetail.Kind.lower(), targetPod,chaosDetails)
