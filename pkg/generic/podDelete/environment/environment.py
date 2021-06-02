# package environment

# import (
# 	"strconv"

# 	clientTypes "k8s.io/apimachinery/pkg/types"

# 	experimentTypes "github.com/litmuschaos/litmus-go/pkg/generic/pod-delete/types"
# 	"github.com/litmuschaos/litmus-go/pkg/types"
# 	"github.com/litmuschaos/litmus-go/pkg/utils/os"
# )
# getenv fetch the env and set the default value, if any

import os
from kubernetes import type
from pkg.generic.podDelete.types import AppDetails

#GetENV fetches all the env variables from the runner pod
def GetENV(experimentDetails):
	experimentDetails.ExperimentName =  os.getenv("EXPERIMENT_NAME", "pod-delete")
	experimentDetails.ChaosNamespace = os.getenv("CHAOS_NAMESPACE", "litmus")
	experimentDetails.EngineName = os.getenv("CHAOSENGINE", "")
	experimentDetails.ChaosDuration, _ = str.Atoi(os.getenv("TOTAL_CHAOS_DURATION", "30"))
	experimentDetails.ChaosInterval = os.getenv("CHAOS_INTERVAL", "10")
	experimentDetails.RampTime, _ = str.Atoi(os.getenv("RAMP_TIME", "0"))
	experimentDetails.ChaosLib = os.getenv("LIB", "litmus")
	experimentDetails.ChaosServiceAccount = os.getenv("CHAOS_SERVICE_ACCOUNT", "")
	experimentDetails.AppNS = os.getenv("APP_NAMESPACE", "")
	experimentDetails.AppLabel = os.getenv("APP_LABEL", "")
	experimentDetails.AppKind = os.getenv("APP_KIND", "")
	experimentDetails.ChaosUID = type.UID(os.getenv("CHAOS_UID", ""))
	experimentDetails.InstanceID = os.getenv("INSTANCE_ID", "")
	experimentDetails.ChaosPodName = os.getenv("POD_NAME", "")
	experimentDetails.Force, _ = str.ParseBool(os.getenv("FORCE", "false"))
	experimentDetails.Delay, _ = str.Atoi(os.getenv("STATUS_CHECK_DELAY", "2"))
	experimentDetails.Timeout, _ = str.Atoi(os.getenv("STATUS_CHECK_TIMEOUT", "180"))
	experimentDetails.TargetPods = os.getenv("TARGET_PODS", "")
	experimentDetails.PodsAffectedPerc, _ = str.Atoi(os.getenv("PODS_AFFECTED_PERC", "0"))
	experimentDetails.Sequence = os.getenv("SEQUENCE", "parallel")
	experimentDetails.TargetContainer = os.getenv("TARGET_CONTAINER", "")

#InitialiseChaosVariables initialise all the global variables
def InitialiseChaosVariables(chaosDetails, experimentDetails):
	appDetails = AppDetails()
	appDetails.AnnotationCheck, _ = str.ParseBool(os.getenv("ANNOTATION_CHECK", "false"))
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
	chaosDetails.Randomness, _ = str.ParseBool(os.getenv("RANDOMNESS", "false"))

