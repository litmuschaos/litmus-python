from kubernetes import type


# ExperimentDetails is for collecting all the experiment-related details
class ExperimentDetails(object):
	def __init__(self, ExperimentName, EngineName, ChaosDuration, ChaosInterval, RampTime, Force, ChaosLib, ChaosServiceAccount,
	    AppNS, AppLabel, AppKind, InstanceID, ChaosNamespace, ChaosPodName, Timeout, Delay, TargetPods, PodsAffectedPerc
		, Sequence, LIBImagePullPolicy, TargetContainer):
		self.ExperimentName      =   ExperimentName 
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
		self.ChaosUID            = type.UID
		self.InstanceID          = InstanceID
		self.ChaosNamespace      = ChaosNamespace
		self.ChaosPodName        = ChaosPodName
		self.Timeout             = Timeout
		self.Delay               = Delay
		self.TargetPods          = TargetPods
		self.PodsAffectedPerc    = PodsAffectedPerc
		self.Sequence            = Sequence
		self.LIBImagePullPolicy  = LIBImagePullPolicy
		self.TargetContainer     = TargetContainer
