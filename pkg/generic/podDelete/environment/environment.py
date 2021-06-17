import os
from pkg.types.types import AppDetails
from pkg.generic.podDelete.types.types import ExperimentDetails

def atoi(string):
    res = 0
 
    # Iterate through all characters of
    #  input string and update result
    for i in range(len(string)):
        res = res * 10 + (ord(string[i]) - ord('0'))
 
    return res

#GetENV fetches all the env variables from the runner pod
def GetENV(experimentDetails):
	experimentDetails.ExperimentName =  os.getenv("EXPERIMENT_NAME", "pod-delete")
	experimentDetails.ChaosNamespace = os.getenv("CHAOS_NAMESPACE", "litmus")
	experimentDetails.EngineName = os.getenv("CHAOSENGINE", "pod-delete")
	experimentDetails.ChaosDuration = atoi(os.getenv("TOTAL_CHAOS_DURATION", "30"))
	experimentDetails.ChaosInterval = os.getenv("CHAOS_INTERVAL", "10")
	experimentDetails.RampTime = atoi(os.getenv("RAMP_TIME", "0"))
	experimentDetails.ChaosLib = os.getenv("LIB", "litmus")
	experimentDetails.ChaosServiceAccount = os.getenv("CHAOS_SERVICE_ACCOUNT", "")
	experimentDetails.AppNS = os.getenv("APP_NAMESPACE", "")
	experimentDetails.AppLabel = os.getenv("APP_LABEL", "")
	experimentDetails.AppKind = os.getenv("APP_KIND", "")
	experimentDetails.ChaosUID = os.getenv("CHAOS_UID", "")
	experimentDetails.InstanceID = os.getenv("INSTANCE_ID", "12345")
	experimentDetails.ChaosPodName = os.getenv("POD_NAME", "")
	experimentDetails.Force = (os.getenv("FORCE", "false") == 'true')
	experimentDetails.Delay = atoi(os.getenv("STATUS_CHECK_DELAY", "2"))
	experimentDetails.Timeout = atoi(os.getenv("STATUS_CHECK_TIMEOUT", "180"))
	experimentDetails.TargetPods = os.getenv("TARGET_PODS", "")
	experimentDetails.PodsAffectedPerc = atoi(os.getenv("PODS_AFFECTED_PERC", "0"))
	experimentDetails.Sequence = os.getenv("SEQUENCE", "parallel")
	experimentDetails.TargetContainer = os.getenv("TARGET_CONTAINER", "")

#InitialiseChaosVariables initialise all the global variables
def InitialiseChaosVariables(chaosDetails, experimentDetails):
	appDetails = AppDetails()
	appDetails.AnnotationCheck = (os.getenv("ANNOTATION_CHECK", "false") == 'true')
	appDetails.AnnotationKey = os.getenv("ANNOTATION_KEY", "litmuschaos.io/chaos")
	appDetails.AnnotationValue = "true"
	appDetails.Kind = experimentDetails.AppKind
	appDetails.Label = experimentDetails.AppLabel
	appDetails.Namespace = experimentDetails.AppNS

	chaosDetails.ChaosNamespace = experimentDetails.ChaosNamespace
	chaosDetails.ChaosPodName = experimentDetails.ChaosPodName
	chaosDetails.ChaosUID = experimentDetails.ChaosUID
	chaosDetails.EngineName = experimentDetails.EngineName
	chaosDetails.ExperimentName = experimentDetails.ExperimentName
	chaosDetails.InstanceID = experimentDetails.InstanceID
	chaosDetails.Timeout = experimentDetails.Timeout
	chaosDetails.Delay = experimentDetails.Delay
	chaosDetails.AppDetail = appDetails
	chaosDetails.ProbeImagePullPolicy = experimentDetails.LIBImagePullPolicy
	chaosDetails.Randomness = (os.getenv("RANDOMNESS", "false") == 'true')

