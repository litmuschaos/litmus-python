
import types
import time
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
from chaoslib.types import MicroservicesStatus, Secrets

from datetime import datetime


def deployment(clients, targetPod, chaosDetails):
	api = create_k8s_api_client(secrets = None)
	v1 = client.AppsV1beta1Api(api)
	try:
		deployList = v1.list_namespaced_deployment(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	except ApiException as e:
		return False, logger.Errorf("no deployment found with matching label, err: %v", e) 
	
	for deploy in range(deployList):
		if deploy.ObjectMeta.Annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue:
			rsOwnerRef = targetPod.OwnerReferences
			for own in range(rsOwnerRef) :
				if own.Kind == "ReplicaSet" :
					err = clients.KubeClient.AppsV1().ReplicaSets(chaosDetails.AppDetail.Namespace).Get(own.Name, v1.GetOptions{})
					if err != None:
						return False, err
					
					ownerRef = rs.OwnerReferences
					for _, own in range(ownerRef):
						if own.Kind == "Deployment" & own.Name == deploy.Name:
							logging.info("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, deploy.Name, deploy.Namespace)
							return True, None
						

def statefulset(clients, targetPod, chaosDetails):
	api = create_k8s_api_client(secrets = None)
	v1 = client.AppsV1beta1Api(api)
	
	stsList = clients.KubeClient.AppsV1().StatefulSets(chaosDetails.AppDetail.Namespace).List(v1.ListOptions{LabelSelector: chaosDetails.AppDetail.Label})
	if err != None or len(stsList.items) == 0:
		return false, logging.Errorf("no statefulset found with matching label, err: %v", err)
	
	for sts in range(stsList.items):
		if sts.ObjectMeta.Annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue :
			ownerRef = targetPod.OwnerReferences
			for own in range(ownerRef):
				if own.Kind == "StatefulSet" & own.Name == sts.Name:
					logging.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, sts.Name, sts.Namespace)
					return true, None

def daemonset(clients, targetPod, chaosDetails):
	api = create_k8s_api_client(secrets = None)
	v1 = client.AppsV1beta1Api(api)
	
	dsList, err = clients.KubeClient.AppsV1().DaemonSets(chaosDetails.AppDetail.Namespace).List(v1.ListOptions{LabelSelector: chaosDetails.AppDetail.Label})
	if err != None or len(dsList.items) == 0:
		return false, logging.Errorf("no daemonset found with matching label, err: %v", err)
	
	for ds in range(dsList.items):
		if ds.ObjectMeta.Annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue:
			ownerRef = targetPod.OwnerReferences
			for own in range(ownerRef):
				if own.Kind == "DaemonSet" & own.Name == ds.Name:
					logging.info("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, ds.Name, ds.Namespace)
					return true, None

def deploymentconfig(clients, targetPod, chaosDetails):
	api = create_k8s_api_client(secrets = None)
	v1 = client.AppsV1beta1Api(api)
	
	gvrdc = schema.GroupVersionResource{
		Group:    "apps.openshift.io",
		Version:  "v1",
		Resource: "deploymentconfigs",
	}
	deploymentConfigList, err = clients.DynamicClient.Resource(gvrdc).Namespace(chaosDetails.AppDetail.Namespace).List(v1.ListOptions{LabelSelector: chaosDetails.AppDetail.Label})
	if err != None or len(deploymentConfigList.items) == 0:
		return false, logging.Errorf("no deploymentconfig found with matching labels, err: %v", err)
	
	for dc in range(eploymentConfigList.items):
		annotations = dc.GetAnnotations()
		if annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue:
			rcOwnerRef = targetPod.OwnerReferences
			for _, own in range(rcOwnerRef):
				if own.Kind == "ReplicationController":
					rc = clients.KubeClient.CoreV1().ReplicationControllers(chaosDetails.AppDetail.Namespace).Get(own.Name, v1.GetOptions{})
					if err != None :
						return false, err
					
					ownerRef = rc.OwnerReferences
					for own in range(ownerRef):
						if own.Kind == "DeploymentConfig" & own.Name == dc.GetName():
							loging.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, dc.GetName(), dc.GetNamespace())
							return true, None


def rollout(clients, targetPod, chaosDetails):
	api = create_k8s_api_client(secrets = None)
	v1 = client.AppsV1beta1Api(api)
	
	gvrro = schema.GroupVersionResource{
		Group:    "argoproj.io",
		Version:  "v1alpha1",
		Resource: "rollouts",
	}
	rolloutList, err = clients.DynamicClient.Resource(gvrro).Namespace(chaosDetails.AppDetail.Namespace).List(v1.ListOptions{LabelSelector: chaosDetails.AppDetail.Label})
	if err != None or len(rolloutList.items) == 0:
		return false, logging.Errorf("no rollouts found with matching labels, err: %v", err)
	
	for ro in rolloutList.items :
		annotations = ro.GetAnnotations()
		if annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue:
			rsOwnerRef = targetPod.OwnerReferences
			for own in range(rsOwnerRef) :
				if own.Kind == "ReplicaSet":
					rs, err = clients.KubeClient.AppsV1().ReplicaSets(chaosDetails.AppDetail.Namespace).Get(own.Name, v1.GetOptions{})
					if err != None :
						return false, err
					
					ownerRef = rs.OwnerReferences
					for own in range(ownerRef):
						if own.Kind == "Rollout" & own.Name == ro.GetName():
							logging.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, ro.GetName(), ro.GetNamespace())
							return true, None


def numbers_to_strings(argument, clients, targetPod,chaosDetails):
    switcher = {
        "deployment": deployment(clients, targetPod,chaosDetails),
        "statefulset": statefulset(clients, targetPod,chaosDetails),
        "daemonset": daemonset(clients, targetPod,chaosDetails),
		"deploymentconfig": deploymentconfig(clients, targetPod,chaosDetails),
		"rollout" : rollout(clients, targetPod,chaosDetails),
    }
    return switcher.get(argument, "%v appkind is not supported",chaosDetails.AppDetail.Kind)
	
# IsPodParentAnnotated check whether the target pod's parent is annotated or not
def IsPodParentAnnotated(clients, targetPod, chaosDetails):

    return numbers_to_strings(chaosDetails.AppDetail.Kind, clients, targetPod,chaosDetails)
