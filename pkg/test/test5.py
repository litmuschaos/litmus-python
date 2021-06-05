import os
import string

def atoi(string):
    res = 0
 
    # Iterate through all characters of
    #  input string and update result
    for i in range(len(string)):
        res = res * 10 + (ord(string[i]) - ord('0'))
 
    return res
#from kubernetes import type
# ExperimentDetails is for collecting all the experiment-related details
class ExperimentDetails(object):
	def __init__(self, ExperimentName=None, EngineName=None, ChaosDuration=None, ChaosInterval=None, RampTime=None, Force=None, ChaosLib=None, ChaosServiceAccount=None,
	    AppNS=None, AppLabel=None, AppKind=None, InstanceID=None, ChaosNamespace=None, ChaosPodName=None, Timeout=None, Delay=None, TargetPods=None, PodsAffectedPerc=None
		, Sequence=None, LIBImagePullPolicy=None, TargetContainer=None):
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
		self.ChaosNamespace      = ChaosNamespace
		self.ChaosPodName        = ChaosPodName
		self.Timeout             = Timeout
		self.Delay               = Delay
		self.TargetPods          = TargetPods
		self.PodsAffectedPerc    = PodsAffectedPerc
		self.Sequence            = Sequence
		self.LIBImagePullPolicy  = LIBImagePullPolicy
		self.TargetContainer     = TargetContainer

#GetENV fetches all the env variables from the runner pod
def GetENV(experimentDetails):
    experimentDetails.ExperimentName =  os.getenv("EXPERIMENT_NAME", "pod-delete")
    experimentDetails.ChaosNamespace = os.getenv("CHAOS_NAMESPACE", "litmus")
    experimentDetails.EngineName = os.getenv("CHAOSENGINE", "")
    experimentDetails.ChaosDuration = atoi(os.getenv("TOTAL_CHAOS_DURATION", "30"))
    experimentDetails.ChaosInterval = os.getenv("CHAOS_INTERVAL", "10")
    experimentDetails.RampTime = atoi(os.getenv("RAMP_TIME", "0"))
    experimentDetails.ChaosLib = os.getenv("LIB", "litmus")
    experimentDetails.ChaosServiceAccount = os.getenv("CHAOS_SERVICE_ACCOUNT", "")
    experimentDetails.AppNS = os.getenv("APP_NAMESPACE", "Oum")
    experimentDetails.AppLabel = os.getenv("APP_LABEL", "")
    experimentDetails.AppKind = os.getenv("APP_KIND", "")
    #experimentDetails.ChaosUID = UID(os.getenv("CHAOS_UID", ""))
    experimentDetails.InstanceID = os.getenv("INSTANCE_ID", "")
    experimentDetails.ChaosPodName = os.getenv("POD_NAME", "")
    experimentDetails.Force = bool(os.getenv("FORCE", "false"))
    experimentDetails.Delay = atoi(os.getenv("STATUS_CHECK_DELAY", "2"))
    experimentDetails.Timeout = atoi(os.getenv("STATUS_CHECK_TIMEOUT", "180"))
    experimentDetails.TargetPods = os.getenv("TARGET_PODS", "")
    experimentDetails.PodsAffectedPerc = atoi(os.getenv("PODS_AFFECTED_PERC", "0"))
    experimentDetails.Sequence = os.getenv("SEQUENCE", "parallel")
    experimentDetails.TargetContainer = os.getenv("TARGET_CONTAINER", "")


    #return experimentDetails

#GetENV fetches all the env variables from the runner pod
def GetENV2(experimentDetails):
    experimentDetails.ExperimentName =  os.getenv("EXPERIMENT_NAME", "pod-delete")
    experimentDetails.ChaosNamespace = os.getenv("CHAOS_NAMESPACE", "litmus")
    experimentDetails.EngineName = os.getenv("CHAOSENGINE", "")
    experimentDetails.ChaosDuration = atoi(os.getenv("TOTAL_CHAOS_DURATION", "30"))
    experimentDetails.ChaosInterval = os.getenv("CHAOS_INTERVAL", "10")
    experimentDetails.RampTime = atoi(os.getenv("RAMP_TIME", "0"))
    experimentDetails.ChaosLib = os.getenv("LIB", "litmus")
    experimentDetails.ChaosServiceAccount = os.getenv("CHAOS_SERVICE_ACCOUNT", "")
    experimentDetails.AppNS = os.getenv("APP_NAMESPACE", "Kale")
    experimentDetails.AppLabel = os.getenv("APP_LABEL", "")
    experimentDetails.AppKind = os.getenv("APP_KIND", "")
    #experimentDetails.ChaosUID = UID(os.getenv("CHAOS_UID", ""))
    experimentDetails.InstanceID = os.getenv("INSTANCE_ID", "")
    experimentDetails.ChaosPodName = os.getenv("POD_NAME", "")
    experimentDetails.Force = bool(os.getenv("FORCE", "false"))
    experimentDetails.Delay = atoi(os.getenv("STATUS_CHECK_DELAY", "2"))
    experimentDetails.Timeout = atoi(os.getenv("STATUS_CHECK_TIMEOUT", "180"))
    experimentDetails.TargetPods = os.getenv("TARGET_PODS", "")
    experimentDetails.PodsAffectedPerc = atoi(os.getenv("PODS_AFFECTED_PERC", "0"))
    experimentDetails.Sequence = os.getenv("SEQUENCE", "parallel")
    experimentDetails.TargetContainer = os.getenv("TARGET_CONTAINER", "")

class MyClass:
    def __init__(self, a=None):
        self.a = a
def myFunction(x):
    x.a = 'oum'
    print(x.a)

myFunction(MyClass)
print(MyClass.a)

#ExperimentDetails = ExperimentDetails()
#logger.info("[PreReq]: Getting the ENV for the %v experiment", experimentsDetails.ExperimentName)
GetENV(ExperimentDetails)
print("Details :", ExperimentDetails.AppNS)
GetENV2(ExperimentDetails)
print("Details2 :", ExperimentDetails.AppNS)
def update(experimentsDetails):
    experimentsDetails.AppNS = "Kale Oum"
    print("Updat {}:", str(experimentsDetails.AppNS))
    #return experimentsDetails
update(ExperimentDetails)
print("Updated :", ExperimentDetails.AppNS)