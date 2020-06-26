"""Utility class for aws init and gathering operations in chaos"""

import time
import logging
import random

import boto3
from boto3 import Session
from chaostest.kubernetes.k8sutils import K8sUtils

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
    def aws_init_local(account_number: str) -> Session:
        session = boto3.Session(profile_name='default')
        return session

    @staticmethod
    def ec2_detach_eks(session: Session, kubecontext : str) -> str:
        logger.info("Getting list of  nodes")
        v1 = K8sUtils.init_k8s_client(kubecontext)
        list_node_ip_addresses = []
        http_nodes = v1.list_node(pretty='true')
        for i in range(len(http_nodes.items) - 1):
            address_list = http_nodes.items[i].status.addresses
            for address in address_list:
                if address.type == 'InternalIP':
                    list_node_ip_addresses.append(address.address)
        ip_selected = random.choice(list_node_ip_addresses)

        ec2_resource = session.resource('ec2')
        response = ec2_resource.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instance_id = ''
        for instance in response:
            if ip_selected == instance.private_ip_address:
                print("Instance Id return " + instance.id)
                instance_id = instance.id
                break
        if not instance_id:
            raise Exception("Not able to get instance id, exiting")
        return instance_id
