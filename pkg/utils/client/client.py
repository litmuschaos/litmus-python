import ast
import os

from distutils.util import strtobool
from kubernetes import client, config
from kubernetes.client import Configuration, V1Pod

class Client(object):

    def __init__(self, kubeContext=None, configurations=None):
        self.kubeContext   = kubeContext
        self.configurations =  configurations
	
    def init_client(self) -> client.CoreV1Api:
        env = os.environ
        if self.kubeContext:
            # config.load_kube_config()
            config.load_kube_config(self.kubeContext)
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
            self.configurations = configuration
            if proxy_url:
                configuration.proxy = proxy_url
            api = client.ApiClient(configuration)
            return client.CoreV1Api(api)

