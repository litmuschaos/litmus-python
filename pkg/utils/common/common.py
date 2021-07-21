
import time, threading
import random
import logging
import os, sys
import signal
import pkg.types.types as types
import pkg.events.events as events
import string
import pkg.result.chaosresult as chaosresult
import pkg.maths.maths as maths
		
#WaitForDuration waits for the given time duration (in seconds)
def WaitForDuration(duration):
	time.sleep(duration)

# RandomInterval wait for the random interval lies between lower & upper bounds
def RandomInterval(interval):
	intervals = interval.split("-")
	lowerBound = 0
	upperBound = 0

	if len(intervals) == 1:
		lowerBound = 0
		upperBound = maths.atoi(intervals[0])
	elif len(intervals) == 2:
		lowerBound = maths.atoi(intervals[0])
		upperBound = maths.atoi(intervals[1])
	else:
		return logging.info("unable to parse CHAOS_INTERVAL, provide in valid format")

	waitTime = lowerBound + random.randint(0, upperBound-lowerBound)
	logging.info("[Wait]: Wait for the random chaos interval %s",(waitTime))
	WaitForDuration(waitTime)
	return None

#GetTargetContainer will fetch the container name from application pod
#This container will be used as target container
def GetTargetContainer(appNamespace, appName, clients):
	
	try:
		pod = clients.clientCoreV1.read_namespaced_pod(name=appName, namespace=appNamespace)
	except Exception as e:
		return "", e
	
	return pod.spec.containers[0].name, None

# GetRunID generate a random
def GetRunID():
	runId = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
	return str(runId)

# Notify Catch and relay certain signal(s) to sendor.
# waiting until the abort signal recieved
def Notify(expname, resultDetails, chaosDetails, eventsDetails, clients):
	
	# initialising result object
	result = chaosresult.ChaosResults()
	logging.info("[Chaos]: Chaos Experiment Abortion started because of terminated signal received")
	
	# updating the chaosresult after stopped
	failStep = "Chaos injection stopped!"
	types.SetResultAfterCompletion(resultDetails, "Stopped", "Stopped", failStep)
	result.ChaosResult(chaosDetails, resultDetails, "EOT", clients)
	
	# generating summary event in chaosengine
	msg = expname + " experiment has been aborted"
	types.SetEngineEventAttributes(eventsDetails, types.Summary, msg, "Warning", chaosDetails)
	events.GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine", clients)

	# generating summary event in chaosresult
	types.SetResultEventAttributes(eventsDetails, types.Summary, msg, "Warning", resultDetails)
	events.GenerateEvents(eventsDetails, chaosDetails, "ChaosResult", clients)

# AbortWatcher continuosly watch for the abort signals
# it will update chaosresult w/ failed step and create an abort event, if it recieved abort signal during chaos
def AbortWatcher(expname, resultDetails, chaosDetails, eventsDetails, clients):
	
	# sendor thread is used to transmit signal notifications.
	sender = threading.Thread(target=Notify, args=(expname, resultDetails, chaosDetails, eventsDetails, clients))
	def signal_handler(sig, frame):
		sender.start()
		sender.join()
		sys.exit(0)
	
	signal.signal(signal.SIGTERM, signal_handler)
	signal.signal(signal.SIGINT, signal_handler)

#GetIterations derive the iterations value from given parameters
def GetIterations(duration, interval):
	iterations = 0
	if interval != 0:
		iterations = duration / interval
	return max(iterations, 1)

# Getenv fetch the env and set the default value, if any
def Getenv(key, defaultValue):
	value = os.Getenv(key)
	if value == "":
		value = defaultValue

	return value

#FilterBasedOnPercentage return the slice of list based on the the provided percentage
def FilterBasedOnPercentage(percentage, list):

	finalList = []
	newInstanceListLength = max(1, maths.Adjustment(percentage, len(list)))
	
	# it will generate the random instanceList
	# it starts from the random index and choose requirement no of volumeID next to that index in a circular way.
	index = random.randint(0, len(list))
	for i in range(newInstanceListLength):
		finalList = finalList.append(list[index])
		index = (index + 1) % len(list)

	return finalList
