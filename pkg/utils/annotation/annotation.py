
import types
import time
from kubernetes.client.api import core_v1_api
from kubernetes.client.models.v1_event import V1Event
from kubernetes import client, config
import time
#import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
from dagster_k8s.client import (
    DagsterK8sAPIRetryLimitExceeded,
    DagsterK8sError,
    DagsterK8sPipelineStatusException,
    DagsterK8sTimeoutError,
    DagsterK8sUnrecoverableAPIError,
)
from datetime import datetime


def deployment(clients, targetPod, chaosDetails):
	api_instance = client.CoreV1Api(clients)
	
	try:
		deployList = api_instance.list_namespaced_deployment(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	except ApiException as e:
		return False, errors.Errorf("no deployment found with matching label, err: %v", e) 
	
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
							log.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, deploy.Name, deploy.Namespace)
							return True, None
						
					
				
			
		
	

def statefulset(clients, targetPod, chaosDetails):
	stsList, err := clients.KubeClient.AppsV1().StatefulSets(chaosDetails.AppDetail.Namespace).List(v1.ListOptions{LabelSelector: chaosDetails.AppDetail.Label})
	if err != nil || len(stsList.Items) == 0 {
		return false, errors.Errorf("no statefulset found with matching label, err: %v", err)
	}
	for _, sts := range stsList.Items {
		if sts.ObjectMeta.Annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue {
			ownerRef := targetPod.OwnerReferences
			for _, own := range ownerRef {
				if own.Kind == "StatefulSet" && own.Name == sts.Name {
					log.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, sts.Name, sts.Namespace)
					return true, nil
				}
			}
		}
	}

def daemonset(clients, targetPod, chaosDetails):
	dsList, err := clients.KubeClient.AppsV1().DaemonSets(chaosDetails.AppDetail.Namespace).List(v1.ListOptions{LabelSelector: chaosDetails.AppDetail.Label})
	if err != nil || len(dsList.Items) == 0 {
		return false, errors.Errorf("no daemonset found with matching label, err: %v", err)
	}
	for _, ds := range dsList.Items {
		if ds.ObjectMeta.Annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue {
			ownerRef := targetPod.OwnerReferences
			for _, own := range ownerRef {
				if own.Kind == "DaemonSet" && own.Name == ds.Name {
					log.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, ds.Name, ds.Namespace)
					return true, nil
				}
			}
		}
	}

def deploymentconfig(clients, targetPod, chaosDetails):
	gvrdc := schema.GroupVersionResource{
		Group:    "apps.openshift.io",
		Version:  "v1",
		Resource: "deploymentconfigs",
	}
	deploymentConfigList, err := clients.DynamicClient.Resource(gvrdc).Namespace(chaosDetails.AppDetail.Namespace).List(v1.ListOptions{LabelSelector: chaosDetails.AppDetail.Label})
	if err != nil || len(deploymentConfigList.Items) == 0 {
		return false, errors.Errorf("no deploymentconfig found with matching labels, err: %v", err)
	}
	for _, dc := range deploymentConfigList.Items {
		annotations := dc.GetAnnotations()
		if annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue {
			rcOwnerRef := targetPod.OwnerReferences
			for _, own := range rcOwnerRef {
				if own.Kind == "ReplicationController" {
					rc, err := clients.KubeClient.CoreV1().ReplicationControllers(chaosDetails.AppDetail.Namespace).Get(own.Name, v1.GetOptions{})
					if err != nil {
						return false, err
					}
					ownerRef := rc.OwnerReferences
					for _, own := range ownerRef {
						if own.Kind == "DeploymentConfig" && own.Name == dc.GetName() {
							log.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, dc.GetName(), dc.GetNamespace())
							return true, nil
						}
					}
				}
			}
		}
	}

def rollout(clients, targetPod, chaosDetails):
	gvrro := schema.GroupVersionResource{
		Group:    "argoproj.io",
		Version:  "v1alpha1",
		Resource: "rollouts",
	}
	rolloutList, err := clients.DynamicClient.Resource(gvrro).Namespace(chaosDetails.AppDetail.Namespace).List(v1.ListOptions{LabelSelector: chaosDetails.AppDetail.Label})
	if err != nil || len(rolloutList.Items) == 0 {
		return false, errors.Errorf("no rollouts found with matching labels, err: %v", err)
	}
	for _, ro := range rolloutList.Items {
		annotations := ro.GetAnnotations()
		if annotations[chaosDetails.AppDetail.AnnotationKey] == chaosDetails.AppDetail.AnnotationValue {
			rsOwnerRef := targetPod.OwnerReferences
			for _, own := range rsOwnerRef {
				if own.Kind == "ReplicaSet" {
					rs, err := clients.KubeClient.AppsV1().ReplicaSets(chaosDetails.AppDetail.Namespace).Get(own.Name, v1.GetOptions{})
					if err != nil {
						return false, err
					}
					ownerRef := rs.OwnerReferences
					for _, own := range ownerRef {
						if own.Kind == "Rollout" && own.Name == ro.GetName() {
							log.Infof("[Info]: chaos candidate of kind: %v, name: %v, namespace: %v", chaosDetails.AppDetail.Kind, ro.GetName(), ro.GetNamespace())
							return true, nil
						}
					}
				}
			}
		}
	}

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
