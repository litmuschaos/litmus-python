
from kubernetes.stream import stream

# PodDetails contains all the required variables to exec inside a container
class PodDetails(object):
	def __init__(self, PodName=None, Namespace=None, ContainerName=None):
		self.PodName       = PodName
		self.Namespace     = Namespace
		self.ContainerName = ContainerName

# checkPodStatus verify the status of given pod & container
def checkPodStatus(pod , containerName):

    if pod.status.phase.lower() != "running":
        return ValueError("{} pod is not in running state, phase: {}".format(pod.Name, pod.Status.Phase))
    
    for container in pod.status.container_statuses:
        if container.name == containerName and not container.ready:
            return ValueError("{} container of {} pod is not in ready state, phase: {}".format(container.name, pod.metadata.name, pod.status.phase))

    return None

def Exec(commandDetails, clients, command):

    try:
        pod = clients.clientCoreV1.read_namespaced_pod(name=commandDetails.PodName, namespace=commandDetails.Namespace)
    except Exception as exp:
       	return "", ValueError("unable to get {} pod in {} namespace, err: {}".format(commandDetails.PodName, commandDetails.Namespace, exp))

    err = checkPodStatus(pod, commandDetails.ContainerName)
    if err != None:
        return "", err

    # Calling exec and waiting for response
    stream(clients.clientCoreV1.connect_get_namespaced_pod_exec,
        commandDetails.PodName,
        commandDetails.Namespace,
        command=command,
        stderr=True, stdin=False,
        stdout=True, tty=False)

    return None

# SetExecCommandAttributes initialise all the pod details  to run exec command
def SetExecCommandAttributes(podDetails , PodName, ContainerName, Namespace):

	podDetails.ContainerName = ContainerName
	podDetails.Namespace = Namespace
	podDetails.PodName = PodName

