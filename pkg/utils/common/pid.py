from kubernetes import client, config
import time
from pkg.types.types import ChaosDetails
import logging
from retry import retry
import logging
from pkg.utils.annotation.annotation import IsPodParentAnnotated
logger = logging.getLogger(__name__)
from chaosk8s import create_k8s_api_client
from chaoslib.types import MicroservicesStatus, Secrets

# CrictlInspectResponse JSON representation of crictl inspect command output
# in crio, pid is present inside pid attribute of inspect output
# in containerd, pid is present inside `info.pid` of inspect output

class Namespaces(object):
	def __init__(self, Type=None, Path=None):
		self.Type = Type
		self.Path = Path

class LinuxAttributes(object):
    def __init__(self, Linux=None):
        self.RuntimeSpec = RuntimeDetails(Linux)

class InfoDetails(object):
    def __init__(self, Namespaces=None):
        self.RuntimeSpec = LinuxAttributes(Namespaces)

class RuntimeDetails(object):
    def __init__(self, Linux=None):
        self.RuntimeSpec = RuntimeDetails(Linux)
         
class InfoDetails(object):
	def __init__(self, PID=None, Linux=None):
		self.RuntimeSpec = RuntimeDetails(Linux)
		self.PID         = PID
         
class CrictlInspectResponse(object): 
    def __init__(self, Info=None):
        self.Info = InfoDetails(Info)


class StateDetails(object):
    def __init__(self, PID=None):
        self.PID = PID

class DockerInspectResponse(object):
    def __init__(self, PID=None):
        self.State = StateDetails(PID)


#GetPID extract out the PID of the target container
def GetPID(runtime, containerID, socketPath):
	PID = 0

	if runtime == "docker":
		host = "unix:#" + socketPath
		# deriving pid from the inspect out of target container
		out, err = exec.Command("sudo", "docker", "--host", host, "inspect", containerID).CombinedOutput()
		if err != None:
			logger.error(fmt.Sprintf("[docker]: Failed to run docker inspect: %s", string(out)))
			return 0, err

		# parsing data from the json output of inspect command
		PID, err = parsePIDFromJSON(out, runtime)
		if err != None {
			logger.error(fmt.Sprintf("[docker]: Failed to parse json from docker inspect output: %s", string(out)))
			return 0, err
		}
	case "containerd", "crio":
		# deriving pid from the inspect out of target container
		endpoint = "unix:#" + socketPath
		out, err = exec.Command("sudo", "crictl", "-i", endpoint, "-r", endpoint, "inspect", containerID).CombinedOutput()
		if err != None {
			logger.error(fmt.Sprintf("[cri]: Failed to run crictl: %s", string(out)))
			return 0, err
		}
		# parsing data from the json output of inspect command
		PID, err = parsePIDFromJSON(out, runtime)
		if err != None {
			logger.Errorf(fmt.Sprintf("[cri]: Failed to parse json from crictl output: %s", string(out)))
			return 0, err
		}
	default:
		return 0, errors.Errorf("%v container runtime not suported", runtime)
	}

	logger.Info(fmt.Sprintf("[Info]: Container ID=%s has process PID=%d", containerID, PID))

	return PID, None
}

#parsePIDFromJSON extract the pid from the json output
def parsePIDFromJSON(j []byte, runtime string):
	var pid int
	# namespaces are present inside `info.runtimeSpec.linux.namespaces` of inspect output
	# linux namespace of type network contains pid, in the form of `/proc/<pid>/ns/net`
	if runtime == "docker":
		# in docker, pid is present inside state.pid attribute of inspect output
		resp []DockerInspectResponse{}
		if err = json.Unmarshal(j, &resp); err != None {
			return 0, err
		}
		pid = resp[0].State.PID
	case "containerd":
		var resp CrictlInspectResponse
		if err = json.Unmarshal(j, &resp); err != None {
			return 0, err
		}
		for _, namespace = range resp.Info.RuntimeSpec.Linux.Namespaces {
			if namespace.Type == "network" {
				value = strings.Split(namespace.Path, "/")[2]
				pid, _ = strconv.Atoi(value)
			}
		}
	case "crio":
		var info InfoDetails
		if err = json.Unmarshal(j, &info); err != None {
			return 0, err
		}
		pid = info.PID
		if pid == 0 {
			var resp CrictlInspectResponse
			if err = json.Unmarshal(j, &resp); err != None {
				return 0, err
			}
			pid = resp.Info.PID
		}
	default:
		return 0, errors.Errorf("[cri]: unsupported container runtime, runtime: %v", runtime)
	}
	if pid == 0 {
		return 0, errors.Errorf("[cri]: No running target container found, pid: %d", pid)
	}

	return pid, None

