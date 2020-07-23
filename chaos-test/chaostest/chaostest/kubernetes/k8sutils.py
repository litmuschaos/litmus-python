"""K8s utility class for initializing k8s client and other utility operations """
import ast
import os

from distutils.util import strtobool
from kubernetes import client, config
from kubernetes.client import Configuration, V1Pod

__author__ = 'Vijay Thomas'


class K8sUtils(object):

    @staticmethod
    def init_k8s_client(kube_context: str) -> client.CoreV1Api:
        env = os.environ
        if kube_context:
            # config.load_kube_config()
            config.load_kube_config(kube_context)
            configuration = Configuration()
            configuration.verify_ssl = bool(strtobool((env.get(
                "KUBERNETES_VERIFY_SSL", "false"))))
            api_client = client.ApiClient(configuration)
            return client.CoreV1Api(api_client)
        elif env.get("CHAOSTOOLKIT_IN_POD") == "true":
            config.load_incluster_config()

            proxy_url = os.getenv('HTTP_PROXY', None)
            if proxy_url:
                configuration = Configuration()
                configuration.proxy = proxy_url
                api_client = client.ApiClient(configuration)
                return client.CoreV1Api(api_client)
            else:
                api = client.ApiClient()
                return client.CoreV1Api(api)

        else:
            configuration = client.Configuration()
            configuration.debug = True
            configuration.host = os.environ.get("KUBERNETES_HOST", "http://localhost")
            configuration.verify_ssl = bool(strtobool((env.get(
                "KUBERNETES_VERIFY_SSL", "false"))))
            configuration.cert_file = os.environ.get("KUBERNETES_CA_CERT_FILE")
            if "KUBERNETES_CERT_FILE" in env:
                configuration.cert_file = os.environ.get("KUBERNETES_CERT_FILE")
                configuration.key_file = os.environ.get("KUBERNETES_KEY_FILE")
            elif "KUBERNETES_USERNAME" in env:
                configuration.username = os.environ.get("KUBERNETES_USERNAME")
                configuration.password = os.environ.get("KUBERNETES_PASSWORD", "")

            proxy_url = os.getenv('HTTP_PROXY', None)
            if proxy_url:
                configuration.proxy = proxy_url
            api = client.ApiClient(configuration)
            return client.CoreV1Api(api)

    @staticmethod
    def get_pod_status(kube_client: client.CoreV1Api, label: str) -> list:
        return kube_client.list_pod_for_all_namespaces(label_selector=label)

    @staticmethod
    def get_node_status(kube_client: client.CoreV1Api, label: str) -> list:
        conditions = []
        if label:
            list_nodes = kube_client.list_node(label_selector=label, pretty='true', _preload_content=False)
            for node in list_nodes:
                conditions = node.conditons
        else:
            list_nodes = kube_client.list_node(pretty='true', _preload_content=False)
            for node in list_nodes:
                conditions = node.conditons
        return conditions
