from distutils.log import error
from re import subn
import boto3, logging
import pkg.utils.client.client as client

# AWS_AZ class is checking the status of LoadBalancer and availablity zone
class AWS_AZ(object):
    def __init__(self, client=None):
        self.clients = client

    # CheckAWSStatus checks target load balancer availability
    def CheckAWSStatus(self, experimentsDetails):
        
        self.clients = client.AWSClient().clientElb
        
        if experimentsDetails.LoadBalancerName == "" or experimentsDetails.LoadBalancerZones == "" :
            return ValueError("Provided LoadBalancer Name or LoadBalanerZoner are empty")
        
        try:
            self.clients.describe_load_balancers()['LoadBalancerDescriptions']
        except Exception as exp:
            return ValueError(exp)
        logging.info("[Info]: LoadBalancer and Availablity of zone has been checked")

    def getSubnetFromVPC(self, experimentsDetails): 
        client = boto3.client('elb')
        try:
            response = client.describe_load_balancers(
                LoadBalancerNames=[
                    experimentsDetails.LoadBalancerName,
                ]
            )
            return (response['LoadBalancerDescriptions'][0]['Subnets'])
        except (self.clients.exceptions.AccessPointNotFoundException, self.clients.exceptions.InvalidConfigurationRequestException) as exp:
            return ValueError(exp)

    def getTargetSubnet(self, experimentsDetails, zone):
        client = boto3.client('ec2')
        try:
            lst=self.getSubnetFromVPC(experimentsDetails)
            i=0
            for i in range(len(lst)):
                response = client.describe_subnets(
                    SubnetIds=[
                        lst[i],
                    ],
                )
                if(response['Subnets'][0]['AvailabilityZone']) == zone:
                    return lst[i], None
        except (self.clients.exceptions.AccessPointNotFoundException, self.clients.exceptions.InvalidConfigurationRequestException) as exp:
            return lst[i], ValueError(exp)


    def detachSubnet(self, experimentsDetails, subnet): 
        client = boto3.client('elb')
        try:
                response = client.detach_load_balancer_from_subnets(
                LoadBalancerName=experimentsDetails.LoadBalancerName,
                Subnets=subnet
            )
                if (response['ResponseMetadata']['HTTPStatusCode']) != "200":
                    ValueError("[Error]: Fail to detach the target subnet %s", subnet)
        except (self.clients.exceptions.AccessPointNotFoundException, self.clients.exceptions.InvalidConfigurationRequestException) as exp:
            return ValueError(exp)

    def attachSubnet(self, experimentsDetails, subnet): 
        client = boto3.client('elb')
        try:
                response = client.attach_load_balancer_to_subnets(
                LoadBalancerName=experimentsDetails.LoadBalancerName,
                Subnets=subnet
            )
                if (response['ResponseMetadata']['HTTPStatusCode']) != "200":
                    ValueError("[Error]: Fail to attach the target subnet %s", subnet)
        except (self.clients.exceptions.AccessPointNotFoundException, self.clients.exceptions.InvalidConfigurationRequestException) as exp:
            return ValueError(exp)
        