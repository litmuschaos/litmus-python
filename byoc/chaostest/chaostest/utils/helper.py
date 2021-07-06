import logging
import os
import subprocess
import time
import json
import yaml
from jinja2 import Environment,  select_autoescape, PackageLoader

__author__ = 'Sumit_Nagal@intuit.com'

logger = logging.getLogger(__name__)


class Helper(object):
    ####################################
    #      Function definitions        #
    ####################################

    TEST_RESULT_STATUS = {
        True: "Pass",
        False: "Failed",
        "Running": "Awaited"
    }

    def run_shell_task(self, cmd_arg_list):
        """
        run_shell_task() runs a shell command and prints the output as it executes.
        It takes a list of strings that comprises the command itself, as the sole arg.
        """
        run_cmd = subprocess.Popen(cmd_arg_list, stdout=subprocess.PIPE, env=os.environ.copy())
        run_cmd.communicate()

    def chaos_result_tracker(self, exp_name, exp_phase, exp_verdict, ns, engineName, jornal_file_name = None):
        """
        chaos_result_tracker() creates/patches the litmus chaosresult custom resource in the provided namespace.
        Typically invoked before and after chaos, and takes the .spec.phase, .spec.verdict & namespace as as args.
        """

        env_tmpl = Environment(loader=PackageLoader('chaostest', 'templates'), trim_blocks=True, lstrip_blocks=True,
                               autoescape=select_autoescape(['yaml']))
        template = env_tmpl.get_template('chaos-result.j2')

        #events = None
        # if jornal_file_name:
        #     if os.path.exists(jornal_file_name):
        #         with open(jornal_file_name, "r") as file:
        #             yaml_content = yaml.dump(json.load(file))
        #             if yaml_content:
        #                 events = "\n" + yaml_content
        #         file.close()
        updated_chaosresult_template = template.render(engineName=engineName, c_experiment=exp_name, phase=exp_phase, verdict=exp_verdict, namespace=ns)
        with open('chaosresult.yaml', "w+") as f:
            f.write(updated_chaosresult_template)
        chaosresult_update_cmd_args_list = ['kubectl', 'apply', '-f', 'chaosresult.yaml', '-n', ns]
        self.run_shell_task(chaosresult_update_cmd_args_list)

    # @staticmethod
    # def get_updated_result_name(experiment_name: str):
    #     result_name = experiment_name 
    #     return result_name
