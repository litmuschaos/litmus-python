import os
from kubernetes import client, config, dynamic
from kubernetes.client import api_client

# Client Class is maintaining clients for k8s
class Client(object):
    def __init__(self, conf=None):
        self.clientk8s      =  client.CoreV1Api(conf)
        self.clientDyn      =  dynamic.DynamicClient(api_client.ApiClient(configuration=conf))
        self.clientApps     =  client.AppsV1Api(conf)
        self.clientsAppsV1  = client.AppsV1beta1Api(conf)

# Config maintain configuration for in and out cluster
class Configs(object):

    def __init__(self, kubeContext=None, configurations=None):
        self.kubeContext    = kubeContext
        self.configurations =  configurations
    
    def get_config(self):

        global configs
        if self.kubeContext != "":
            configs = self.kubeContext
        elif os.getenv('KUBERNETES_SERVICE_HOST'):
    	    configs = config.load_incluster_config()
        else:
	        configs = config.load_kube_config()
        
        self.configurations = configs
        return configs
