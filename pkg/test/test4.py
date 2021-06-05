from retry import retry

from kubernetes import client, config
from chaosk8s import create_k8s_api_client
from chaoslib.types import MicroservicesStatus, Secrets
from kubernetes.client.rest import ApiException
import random

# ENVDetails contains the ENV details
class ENVDetails(object):
	def __init__(self):
		self.ENV = []

	def append(self, value):
		self.ENV.append(value)

# SetEnv sets the env inside envDetails struct
envDetails = ENVDetails()
def getEnvSource():
    downwardENV = client.V1EnvVarSource(field_ref=client.V1ObjectFieldSelector(field_path="metadata.name"))
    return downwardENV
	#return envDetails

#SetEnv("APP_NS", "litmus")
#SetEnv("APP_NS", "litmus")
ret = getEnvSource()
envDetails.append(client.V1EnvVar(name="POD_NAME", value_from=ret))
print("Return : ", ret)
print("test list :", envDetails.ENV)
# class Test(object): 
#     tri = 0
#     def __init__(self, appNs=None, test=None):
#         self.appNs = appNs
#         self.Test2 = Test2(test)
#         self.test_max_delay = retry(exceptions=Exception,max_delay=2*appNs,tries=appNs, delay=appNs/2, backoff=0)(self.test_max_delay)
#     def test_max_delay(self):
#         try:
#              print("Tess")
#              val = 1/0
#         except Exception as e:
#             raise Exception
#         return None
#     def getTest2(self):
#         return self.Test2
# #Adjustment contains rule of three for calculating an integer given another integer representing a percentage
# def Adjustment(a, b):
# 	return (a * b / 100)
# print("Adjustment", Adjustment(10,2))

# fen = Test(appNs=8, test=['2','2'])
# val = random.randint(0, 5-2)
# print("Value : ", val)
# #def Value(value):
# #    value.getTest2().test = '9'
# #    return value
# #    print("Value :", value.getTest2().test)
# print("Vale : ",fen.appNs)
# print("return ", fen.Test2.test)
# # err = fen.test_max_delay()
# # print("Err", err)
