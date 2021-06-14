import experiments.generic.podDelete.podDelete as podDelete
import argparse
parser = argparse.ArgumentParser()

def main():

	# parse the experiment name
	parser.add_argument("-experimentName", action='store',
                    default="pod-delete",
                    dest="experimentName",
                    help="Chaos experiment to chose for execution"
                    )
	args = parser.parse_args()
	print("Experiment Name: {}".format(args.experimentName))

	# invoke the corresponding experiment based on the the (-name) flag
	if args.experimentName == "pod-delete":
		podDelete.PodDelete()
	else:
		print("Unsupported -name {}, please provide the correct value of -name args".format(args.experimentName))
	return

main()