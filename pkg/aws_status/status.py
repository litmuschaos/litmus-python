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

    # detachAZfromLB detaching availablity zone from load balancer
    def detachAZfromLB(self, experimentsDetails, zone): 
        self.clients = client.AWSClient().clientElb 
        try:
            self.clients.disable_availability_zones_for_load_balancer(
                LoadBalancerName=experimentsDetails.LoadBalancerName,
                AvailabilityZones=[
                    zone,
                ]
            )

        except (self.clients.exceptions.AccessPointNotFoundException, self.clients.exceptions.InvalidConfigurationRequestException) as exp:
            return ValueError(exp)
    
    # attachAZtoLB attaching availablity zone from load balancer
    def attachAZtoLB(self, experimentsDetails, zone):
        self.clients = client.AWSClient().clientElb
        try:
            self.clients.enable_availability_zones_for_load_balancer(
                LoadBalancerName=experimentsDetails.LoadBalancerName,
                AvailabilityZones=[
                    zone,
                ]
            )
        except (self.clients.exceptions.AccessPointNotFoundException, self.clients.exceptions.InvalidConfigurationRequestException) as exp:
            return ValueError(exp)
