# ExperimentDetails is for collecting all the experiment-related details
class ExperimentDetails(object):
	def __init__(self, ExperimentName=None, EngineName=None, ChaosDuration=None, ChaosInterval=None, RampTime=None, Force=None, ChaosLib=None, 
		ChaosServiceAccount=None, AppNS=None, AppLabel=None, AppKind=None, InstanceID=None, ChaosNamespace=None, ChaosPodName=None, Timeout=None, 
		Delay=None, TargetPods=None, PodsAffectedPerc=None, Sequence=None, LIBImagePullPolicy=None, TargetContainer=None, UID=None):
		self.ExperimentName      = ExperimentName 
		self.EngineName          = EngineName
		self.ChaosDuration       = ChaosDuration
		self.ChaosInterval       = ChaosInterval
		self.RampTime            = RampTime
		self.Force               = Force
		self.ChaosLib            = ChaosLib
		self.ChaosServiceAccount = ChaosServiceAccount
		self.AppNS               = AppNS
		self.AppLabel            = AppLabel
		self.AppKind             = AppKind
		self.InstanceID          = InstanceID
		self.ChaosUID            = UID
		self.ChaosNamespace      = ChaosNamespace
		self.ChaosPodName        = ChaosPodName
		self.Timeout             = Timeout
		self.Delay               = Delay
		self.TargetPods          = TargetPods
		self.PodsAffectedPerc    = PodsAffectedPerc
		self.Sequence            = Sequence
		self.LIBImagePullPolicy  = LIBImagePullPolicy
		self.TargetContainer     = TargetContainer