
import time
import random
import logging
logger = logging.getLogger(__name__)
import os
from kubernetes import client
import signal

# ENVDetails contains the ENV details
class ENVDetails(object):
	def __init__(self):
		self.ENV = []

	def append(self, value):
		self.ENV.append(value)
		
#WaitForDuration waits for the given time duration (in seconds)
def WaitForDuration(duration):
	time.sleep(duration)

#Atoi stands for ASCII to Integer Conversion
def atoi(string):
    res = 0

    # Iterate through all characters of
    #  input and update result
    for i in range(len(string)):
        res = res * 10 + (ord(string[i]) - ord('0'))
 
    return res

# RandomInterval wait for the random interval lies between lower & upper bounds
def RandomInterval(interval):
	intervals = interval.split("-")
	lowerBound = 0
	upperBound = 0

	if len(intervals) == 1:
		lowerBound = 0
		upperBound, _ = atoi(intervals[0])
	elif len(intervals) == 2:
		lowerBound, _ = atoi(intervals[0])
		upperBound, _ = atoi(intervals[1])
	else:
		return logger.error("unable to parse CHAOS_INTERVAL, provide in valid format")

	#rand.Seed(time.Now().UnixNano())
	waitTime = lowerBound + random.randint(0, upperBound-lowerBound)
	logger.Infof("[Wait]: Wait for the random chaos interval %vs", waitTime)
	WaitForDuration(waitTime)
	return None

# GetRunID generate a random
def GetRunID():
	#letterRunes = []rune("abcdefghijklmnopqrstuvwxyz")
	#runID = make([]rune, 6)
	rand.Seed(time.Now().UnixNano())
	for i in range(runID):
		runID[i] = letterRunes[random.randint(0, len(letterRunes))]

	return(runID)

# AbortWatcher continuosly watch for the abort signals
# it will update chaosresult w/ failed step and create an abort event, if it recieved abort signal during chaos
def AbortWatcher(expname, clients, resultDetails, chaosDetails, eventsDetails):
	AbortWatcherWithoutExit(expname, clients, resultDetails, chaosDetails, eventsDetails)
	os.Exit(1)

# AbortWatcherWithoutExit continuosly watch for the abort signals
def AbortWatcherWithoutExit(expname, clients, resultDetails, chaosDetails, eventsDetails):

	# signChan channel is used to transmit signal notifications.
	#signChan = make(chan signal.signal, 1)
	# Catch and relay certain signal(s) to signChan channel.
	signal.Notify(signChan, os.Interrupt, syscall.SIGTERM)

	# waiting until the abort signal recieved
	#<-signChan

	logger.Info("[Chaos]: Chaos Experiment Abortion started because of terminated signal received")
	# updating the chaosresult after stopped
	failStep = "Chaos injection stopped!"
	types.SetResultAfterCompletion(resultDetails, "Stopped", "Stopped", failStep)
	result.ChaosResult(chaosDetails, clients, resultDetails, "EOT")

	# generating summary event in chaosengine
	msg = expname + " experiment has been aborted"
	types.SetEngineEventAttributes(eventsDetails, types.Summary, msg, "Warning", chaosDetails)
	events.GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")

	# generating summary event in chaosresult
	types.SetResultEventAttributes(eventsDetails, types.Summary, msg, "Warning", resultDetails)
	events.GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosResult")

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

#Adjustment contains rule of three for calculating an integer given another integer representing a percentage
def Adjustment(a, b):
	return (a * b) / 100

#FilterBasedOnPercentage return the slice of list based on the the provided percentage
def FilterBasedOnPercentage(percentage, list):

	finalList = []
	newInstanceListLength = max(1, Adjustment(percentage, len(list)))
	#rand.Seed(time.Now().UnixNano())

	# it will generate the random instanceList
	# it starts from the random index and choose requirement no of volumeID next to that index in a circular way.
	index = random.randint(0, len(list))
	for i in range(newInstanceListLength):
		finalList = finalList.append(list[index])
		index = (index + 1) % len(list)

	return finalList

# SetEnv sets the env inside envDetails struct
def SetEnv(envDetails, key, value):
	if value != "" :
		envDetails.append(client.V1EnvVar(name=key, value=value))

# SetEnvFromDownwardAPI sets the downapi env in envDetails struct
def SetEnvFromDownwardAPI(envDetails, apiVersion, fieldPath):
	if apiVersion != "" & fieldPath != "" :
		# Getting experiment pod name from downward API
		experimentPodName = getEnvSource(apiVersion, fieldPath)
		envDetails.append(client.V1EnvVar(name="POD_NAME", value_from=experimentPodName))

# getEnvSource return the env source for the given apiVersion & fieldPath
def getEnvSource(apiVersion, fieldPath):
	downwardENV = client.V1EnvVarSource(field_ref=client.V1ObjectFieldSelector(api_version=apiVersion,field_path=fieldPath))
	return downwardENV