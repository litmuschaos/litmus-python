
import os
import pkg.types.types as types
import pkg.maths.maths as maths

#GetENV fetches all the env variables from the runner pod
def GetENV(experimentDetails):
	experimentDetails.ExperimentName =  os.getenv("EXPERIMENT_NAME", "pod-delete")
	experimentDetails.ChaosNamespace = os.getenv("CHAOS_NAMESPACE", "litmus")
	experimentDetails.EngineName = os.getenv("CHAOSENGINE", "")
	experimentDetails.ChaosDuration = maths.atoi(os.getenv("TOTAL_CHAOS_DURATION", "30"))
	experimentDetails.ChaosInterval = os.getenv("CHAOS_INTERVAL", "10")
	experimentDetails.RampTime = maths.atoi(os.getenv("RAMP_TIME", "0"))
	experimentDetails.ChaosLib = os.getenv("LIB", "litmus")
	experimentDetails.AppNS = os.getenv("APP_NAMESPACE", "")
	experimentDetails.AppLabel = os.getenv("APP_LABEL", "")
	experimentDetails.AppKind = os.getenv("APP_KIND", "")
	experimentDetails.ChaosUID = os.getenv("CHAOS_UID", "")
	experimentDetails.InstanceID = os.getenv("INSTANCE_ID", "")
	experimentDetails.ChaosPodName = os.getenv("POD_NAME", "")
	experimentDetails.Force = (os.getenv("FORCE", "false") == 'true')
	experimentDetails.Delay = maths.atoi(os.getenv("STATUS_CHECK_DELAY", "2"))
	experimentDetails.Timeout = maths.atoi(os.getenv("STATUS_CHECK_TIMEOUT", "180"))
	experimentDetails.TargetPods = os.getenv("TARGET_PODS", "")
	experimentDetails.PodsAffectedPerc = maths.atoi(os.getenv("PODS_AFFECTED_PERC", "0"))
	experimentDetails.Sequence = os.getenv("SEQUENCE", "parallel")
	experimentDetails.TargetContainer = os.getenv("TARGET_CONTAINER", "")

#InitialiseChaosVariables initialise all the global variables
def InitialiseChaosVariables(chaosDetails, experimentDetails):
	appDetails = types.AppDetails()
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
	chaosDetails.Randomness = (os.getenv("RANDOMNESS", "false") == 'true')

