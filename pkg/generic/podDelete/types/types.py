from kubernetes import type


# ExperimentDetails is for collecting all the experiment-related details
class ExperimentDetails(object):
	def __init__(self, ExperimentName=None, EngineName=None, ChaosDuration=None, ChaosInterval=None, RampTime=None, Force=None, ChaosLib=None, ChaosServiceAccount=None,
	    AppNS=None, AppLabel=None, AppKind=None, InstanceID=None, ChaosNamespace=None, ChaosPodName=None, Timeout=None, Delay=None, TargetPods=None, PodsAffectedPerc=None
		, Sequence=None, LIBImagePullPolicy=None, TargetContainer=None):
		self.ExperimentName      = None 
		self.EngineName          = None
		self.ChaosDuration       = None
		self.ChaosInterval       = None
		self.RampTime            = None
		self.Force               = None
		self.ChaosLib            = None
		self.ChaosServiceAccount = None
		self.AppNS               = None
		self.AppLabel            = None
		self.AppKind             = None
		self.ChaosUID            = type.UID
		self.InstanceID          = None
		self.ChaosNamespace      = None
		self.ChaosPodName        = None
		self.Timeout             = None
		self.Delay               = None
		self.TargetPods          = None
		self.PodsAffectedPerc    = None
		self.Sequence            = None
		self.LIBImagePullPolicy  = None
		self.TargetContainer     = None
