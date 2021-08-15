#!/usr/bin/env python3

import experiments.generic.pod_delete.pod_delete as pod_delete
import argparse
import logging
import pkg.utils.client.client as client
logging.basicConfig(format='time=%(asctime)s level=%(levelname)s  msg=%(message)s', level=logging.INFO)  

def main():
	parser = argparse.ArgumentParser()
	
	# parse the experiment name
	parser.add_argument("-name", action='store', default="pod-delete", dest="name", help="Chaos experiment for execution")
	# parse the kubeconfig
	parser.add_argument("-kubeconfig", required=False, default="", dest='kubeconfig', help="Absolute path to the kubeconfig file")
	args = parser.parse_args()
	
	#Getting kubeConfig and Generate ClientSets
	config = client.Configuration(kubeconfig=args.kubeconfig)
	clients = client.K8sClient(conf = config.get_config())
	logging.info("Experiment Name: %s", args.name)

	# invoke the corresponding experiment based on the the (-name) flag
	if args.name == "pod-delete":
		pod_delete.PodDelete(clients)
	else:
		logging.error("Unsupported -name %s, please provide the correct value of -name args", args.name)
	return
if __name__ == "__main__":
	main()
