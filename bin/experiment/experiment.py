#!/usr/bin/env python3

import experimentList.generic.podDelete.podDelete as podDelete
import argparse
import os
def main():
	print("1")
	parser = argparse.ArgumentParser()
	# parse the experiment name
	parser.add_argument("-experimentName", action='store',
                    default="pod-delete",
                    dest="experimentName",
                    help="Chaos experiment to chose for execution"
                    )
	parser.add_argument("-kubeContext",
                    required=False,
                    default=os.environ.get("KUBECONFIG", ""),
                    dest='kubeContext',
                    help="Kubernetes client ignore SSL")
	args = parser.parse_args()
	print("1")

	print("Experiment Name: {}".format(args.experimentName))

	# invoke the corresponding experiment based on the the (-name) flag
	if args.experimentName == "pod-delete":
		podDelete.PodDelete()
	else:
		print("Unsupported -name {}, please provide the correct value of -name args".format(args.experimentName))
	return
print("0")
if __name__ == "__main__":
	print("Let's Start!")
	main()
	print("Last")