from kubernetes import client, config
import time
import logging
import logging
logger = logging.getLogger(__name__)
from chaosk8s import create_k8s_api_client
from jinja2 import Environment,  select_autoescape, PackageLoader
import os
import subprocess
import pkg.events.events as events
import pkg.types.types as types
from kubernetes import client, config, dynamic
from kubernetes.client import api_client
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api

from pkg.utils.client.client import Client
global conf
if os.getenv('KUBERNETES_SERVICE_HOST'):
	conf = config.load_incluster_config()
else:
	conf = config.load_kube_config()
class ChaosResults(object):

	def Checkresults(self, chaosDetails, resultDetails , state, iter):
		clientDyn = dynamic.DynamicClient(
			api_client.ApiClient(configuration=conf)
		)
		resultList = {}
		items = 0
		try:
			time.sleep(2)
			if iter < 10:
				chaosResults = clientDyn.resources.get(api_version="litmuschaos.io/v1alpha1", kind="ChaosResult").get()
				if len(chaosResults.items) == 0:
					raise Exception
				for result in chaosResults.items:
					if result.metadata.labels["name"] == resultDetails.Name:
						resultList[items] = result
						items = items + 1
				return resultList
		except Exception as e:
			if e != None:
				self.Checkresults(chaosDetails, resultDetails , state, iter = iter + 2)
		return resultList

	#ChaosResult Create and Update the chaos result
	def ChaosResult(self, chaosDetails, resultDetails , state):
		
		v1 = client.CoreV1Api()

		experimentLabel = {}
		
		# It will list all the chaos-result with matching label
		# it will retries until it got chaos result list or met the timeout(3 mins)
		# Note: We have added labels inside chaos result and looking for matching labels to list the chaos-result
		#var resultList *v1alpha1.ChaosResultList
		resultList = self.Checkresults(chaosDetails, resultDetails , state, 0)

		# as the chaos pod won't be available for stopped phase
		# skipping the derivation of labels from chaos pod, if phase is stopped
		if chaosDetails.EngineName != "" and resultDetails.Phase != "Stopped" :
			# Getting chaos pod label and passing it in chaos result
			try:
				chaosPod = v1.read_namespaced_pod(chaosDetails.ChaosPodName, chaosDetails.ChaosNamespace)
			except Exception as e:
				return print("failed to find chaos pod with name: {}, err: {}".format(chaosDetails.ChaosPodName, e))

			experimentLabel = chaosPod.metadata.labels
		experimentLabel["name"] = resultDetails.Name
		
		# if there is no chaos-result with given label, it will create a new chaos-result
		if len(resultList) == 0 :
			return self.InitializeChaosResult(chaosDetails,  resultDetails, chaosResultLabel =  experimentLabel)
		
		# the chaos-result is already present with matching labels
		# it will patch the new parameters in the same chaos-result
		if state == "SOT" :
			return self.PatchChaosResult(resultList[0],  chaosDetails, resultDetails,chaosResultLabel =  experimentLabel)

		# # it will patch the chaos-result in the end of experiment
		resultDetails.Phase == "Completed"
		return self.PatchChaosResult(resultList[0],  chaosDetails, resultDetails, chaosResultLabel =  experimentLabel)

	#InitializeChaosResult or patch the chaos result
	def InitializeChaosResult(self, chaosDetails , resultDetails , chaosResultLabel, 
		probeStatus = "Wait", passedRuns = 0,  failedRuns = 0, stoppedRuns = 0, probeSuccessPercentage = "Awaited") :
		
		
		env_tmpl = Environment(loader=PackageLoader('pkg', 'templates'), trim_blocks=True, lstrip_blocks=True,
								autoescape=select_autoescape(['yaml']))
		template = env_tmpl.get_template('chaos-result.j2')
		updated_chaosresult_template = template.render(name=resultDetails.Name, namespace=chaosDetails.ChaosNamespace, labels=chaosResultLabel,
													engineName=chaosDetails.EngineName, experimentName=chaosDetails.ExperimentName, instanceID=chaosDetails.InstanceID, phase=resultDetails.Phase, 
												verdict=resultDetails.Verdict, probeStatus=probeStatus, passedRuns = passedRuns,  failedRuns = failedRuns, stoppedRuns = stoppedRuns, probeSuccessPercentage=probeSuccessPercentage)
		with open('chaosresult.yaml', "w+") as f:
			f.write(updated_chaosresult_template)
		
		# if the chaos result is already present, it will patch the new parameters with the existing chaos result CR
		# Note: We have added labels inside chaos result and looking for matching labels to list the chaos-result
		# these labels were not present inside earlier releases so giving a retry/update if someone have a exiting result CR
		# in his cluster, which was created earlier with older release/version of litmus.
		# it will override the params and add the labels to it so that it will work as desired.
		chaosresult_update_cmd_args_list = ['kubectl', 'apply', '-f', 'chaosresult.yaml', '-n', chaosDetails.ChaosNamespace]
		run_cmd = subprocess.Popen(chaosresult_update_cmd_args_list, stdout=subprocess.PIPE, env=os.environ.copy())
		run_cmd.communicate()	
	
		return None

	#GetProbeStatus fetch status of all probes
	def GetProbeStatus(self, resultDetails):
		isAllProbePassed = True

		probeStatus = []
		for probe in resultDetails.ProbeDetails:
			probes = types.ProbeStatus
			probes.Name = probe.Name
			probes.Type = probe.Type
			probes.Status = probe.Status
			probeStatus = probeStatus.append(probes)
			if probe.Phase == "Failed":
				isAllProbePassed = False

		return isAllProbePassed, probeStatus

	#PatchChaosResult Update the chaos result
	def PatchChaosResult(self, result, chaosDetails, resultDetails, chaosResultLabel):

		passedRuns = 0 
		failedRuns = 0 
		stoppedRuns = 0
		isAllProbePassed, probeStatus = self.GetProbeStatus(resultDetails)
		if resultDetails.Phase.lower() == "completed":
			if isAllProbePassed == False:
				resultDetails.Verdict = "Fail"
			if resultDetails.Verdict.lower() == "pass":
				probeSuccessPercentage = "100"
				passedRuns = result.status.history.passedRuns + 1
			elif resultDetails.Verdict.lower() == "fail":
				failedRuns =  result.status.history.failedRuns + 1
				probeSuccessPercentage = "0"
			elif resultDetails.Verdict.lower() == "stopped":
				stoppedRuns = result.status.history.stoppedRuns + 1
				probeSuccessPercentage = "0"
		else:
			probeSuccessPercentage = "Awaited"

		# It will update the existing chaos-result CR with new values
		return self.InitializeChaosResult(chaosDetails, resultDetails, chaosResultLabel, 
		probeStatus, passedRuns, failedRuns, stoppedRuns, probeSuccessPercentage)

	# SetResultUID sets the ResultUID into the ResultDetails structure
	def SetResultUID(self, resultDetails, chaosDetails):
		clientDyn = dynamic.DynamicClient(
			api_client.ApiClient(configuration=conf)
		)
		
		try:
			chaosResults = clientDyn.resources.get(api_version="litmuschaos.io/v1alpha1", kind="ChaosResult").get()
			if len(chaosResults.items) == 0:
				raise Exception
			for result in chaosResults.items:
				if result.metadata.name == resultDetails.Name:
					resultDetails.ResultUID = result.metadata.uid
					return None
		except Exception as err:
			return err

	# #RecordAfterFailure update the chaosresult and create the summary events
	def RecordAfterFailure(self, chaosDetails, resultDetails , failStep , eventsDetails):

		# update the chaos result
		types.SetResultAfterCompletion(resultDetails, "Fail", "Completed", failStep)
		self.ChaosResult(chaosDetails,  resultDetails, "EOT")

		# add the summary event in chaos result
		msg = "experiment: " + chaosDetails.ExperimentName + ", Result: " + resultDetails.Verdict
		types.SetResultEventAttributes(eventsDetails, types.FailVerdict, msg, "Warning", resultDetails)
		events.GenerateEvents(eventsDetails,  chaosDetails, "ChaosResult")

		# add the summary event in chaos engine
		if chaosDetails.EngineName != "":
			types.SetEngineEventAttributes(eventsDetails, types.Summary, msg, "Warning", chaosDetails)
			events.GenerateEvents(eventsDetails,  chaosDetails, "ChaosEngine")

