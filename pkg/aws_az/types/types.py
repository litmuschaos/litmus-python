# ExperimentDetails is for collecting all the experiment-related details
class ExperimentDetails(object):
	def __init__(self, ExperimentName=None, EngineName=None, ChaosDuration=None, ChaosInterval=None, RampTime=None, Force=None, ChaosLib=None, 
		AWSZones=None, AWSRegion=None, AppNS=None, AppLabel=None, AppKind=None, InstanceID=None, ChaosNamespace=None, ChaosPodName=None, Timeout=None, 
		Delay=None, LoadBalancerName= None, LIBImagePullPolicy=None, LoadBalancerNameARN=None, LoadBalancerZones=None, UID=None, VPCType=None):
		self.ExperimentName      = ExperimentName 
		self.EngineName          = EngineName
		self.ChaosDuration       = ChaosDuration
		self.ChaosInterval       = ChaosInterval
		self.RampTime            = RampTime
		self.ChaosLib            = ChaosLib
		self.AppNS               = AppNS
		self.AppLabel            = AppLabel
		self.AppKind             = AppKind
		self.InstanceID          = InstanceID
		self.ChaosUID            = UID
		self.ChaosNamespace      = ChaosNamespace
		self.ChaosPodName        = ChaosPodName
		self.Timeout             = Timeout
		self.Delay               = Delay
		self.LIBImagePullPolicy  = LIBImagePullPolicy
		self.AWSRegion		 = AWSRegion
		self.LoadBalancerName	 = LoadBalancerName
		self.LoadBalancerZones 	 = LoadBalancerZones
		self.LoadBalancerNameARN = LoadBalancerNameARN
