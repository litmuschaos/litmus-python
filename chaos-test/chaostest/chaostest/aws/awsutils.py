"""Utility class for aws init and gathering operations in chaos"""

import time
import logging
import random

import boto3
from boto3 import Session
from chaostest.kubernetes.k8sutils import K8sUtils
from chaostest.utils.chaos_custom_exception import ChaosTestException
from kubernetes.client import V1Pod

logger = logging.getLogger(__name__)

__author__ = 'Vijay Thomas'


class AwsUtils(object):

    @staticmethod
    def aws_init_by_role(account_number: str, role: str, region: str) -> Session:
        """Initializing AWS client for Chaos instance related operations"""
        sts_client = boto3.client('sts')
        assumed_role_object = sts_client.assume_role(
            DurationSeconds=3600,
            RoleArn="arn:aws:iam::" + account_number + ":role/" + role,
            RoleSessionName="ChaosSession" + str(int(round(time.time() * 1000)))
        )
        credentials = assumed_role_object['Credentials']

        session = boto3.Session(
            region_name=region,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )
        return session

    @staticmethod
    def aws_init_local(profile_name: str = "default") -> Session:
        session = boto3.Session(profile_name=profile_name)
        return session

    @staticmethod
    def ec2_detach_eks(session: Session, kubecontext : str, namespace: str, label_name : str) -> str:
        logger.info("Getting list of  pods for namespace " + namespace)
        v1 = K8sUtils.init_k8s_client(kubecontext)

        ip_address_list = []
        v1podlist = v1.list_namespaced_pod(namespace, label_selector=label_name).items

        if not v1podlist:
            raise ChaosTestException("No pods are there in the namespace which was provided " + namespace)
        if len(v1podlist) == 0:
            raise ChaosTestException("List of pods is empty for namespace " + namespace)
        for v1pod in v1podlist:
            if v1pod.status.phase == "Running":
                ip_address_list.append(v1pod.status.host_ip)

        if len(ip_address_list) == 0:
            raise ChaosTestException("nodes are not present matching pod label " + label_name)
        ip_address_list = list(dict.fromkeys(ip_address_list))
        # list_node_ip_addresses = []
        # http_nodes = v1.list_node(pretty='true')
        #
        # for i in range(len(http_nodes.items) - 1):
        #     address_list = http_nodes.items[i].status.addresses
        #     for address in address_list:
        #         if address.type == 'InternalIP':
        #             list_node_ip_addresses.append(address.address)
        ip_selected = random.choice(ip_address_list)

        ec2_resource = session.resource('ec2')
        response = ec2_resource.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instance_id = ''
        for instance in response:
            if ip_selected == instance.private_ip_address:
                logger.info("Instance Id returned " + instance.id)
                instance_id = instance.id
                break
        if not instance_id:
            raise Exception("Not able to get instance id, exiting")
        return instance_id

    @staticmethod
    def validate_iam_role_for_chaos(role_name: str, session: Session):
        try:
            client = session.client("iam")
            response = client.get_role(
                RoleName=role_name
            )
            return response
        except Exception as ex:
            raise ChaosTestException("Role provided " + role_name + " resulted in exception => " + str(ex) +
                                     " Please create role with STS , and required privileges for the test")
