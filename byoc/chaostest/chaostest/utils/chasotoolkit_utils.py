"""Chaos toolkit runner and report class"""
import argparse
import functools
import json
import logging
import os
import site
import sys
from datetime import datetime

import click
from chaoslib.control import load_global_controls
from chaoslib.exceptions import InvalidSource
from chaoslib.experiment import run_experiment
from chaoslib.loader import load_experiment
from chaostest.utils.helper import Helper
from chaostest.utils.report import Report
from chaostoolkit import encoder

logger = logging.getLogger(__name__)

__author__ = 'Vijay_Thomas@intuit.com'

environment_params_for_test = {}


def update_test_chaos_params(key, value):
    environment_params_for_test[key] = value
    os.environ[key] = value


def clear_test_chaos_params():
    environment_params_for_test.clear()
    os.environ.clear()


def chaos_result_decorator(function):
    """
        For updating chaos results in tests, we would need to annotate this to test method. This would take care
        of creating and updating chaosresult object before test run, and once the tests are completed.
    :param function:
    :return:
    """
    @functools.wraps(function)
    def inner(*args, **kwargs):
        experiment_name = os.environ.get("EXP", None)
        time_now = datetime.now()
        time_string = time_now.strftime("%d-%m-%Y-%H-%M-%S-%p")
        time_string = time_string.swapcase()

        result_name = experiment_name + "-" + time_string
        namespace = os.environ.get("NAME_SPACE", None)
        engineName = os.environ.get("CHAOSENGINE", experiment_name)
        test_json = os.environ.get("FILE", "")
        test_result = False
        if experiment_name and namespace and test_json:
            logger.info("Decorators are applied, will update chaos results from here:")
            helper = Helper()
            journal_file_name = "journal-" + test_json
            # if os.path.exists(journal_file_name):
            #     logger.info("Pre existing journal file for the experiment, renaming the same")
            #     backup_journal_file = journal_file_name + "-" + time_string
            #     logger.info("Renaming existing journal file " + journal_file_name + " to " + backup_journal_file)
            #     os.rename(journal_file_name, journal_file_name + "-" + time_string)
            helper.chaos_result_tracker(result_name, 'Running', Helper.TEST_RESULT_STATUS.get("Running"),
                                        namespace, engineName, journal_file_name)
            try:
                test_result = function(*args, **kwargs)
                logger.info("Test result status came as")
                logger.info(test_result)
                if not isinstance(test_result, bool) and isinstance(test_result, str):
                    helper.chaos_result_tracker(result_name, 'Completed', test_result, namespace, engineName, journal_file_name)
                elif not isinstance(test_result, bool) and not isinstance(test_result, str):
                    helper.chaos_result_tracker(result_name, 'Completed', "test_result_not_a_readable_return",
                                                namespace, engineName, journal_file_name)
                else:
                    helper.chaos_result_tracker(result_name, 'Completed',
                                                Helper.TEST_RESULT_STATUS.get(test_result, lambda : test_result),
                                                namespace, engineName, journal_file_name)
                return test_result
            except Exception as ex:
                logger.error("Test Failed with exception " + str(ex))
                helper.chaos_result_tracker(result_name, 'Completed', Helper.TEST_RESULT_STATUS.get(False),
                                            namespace, engineName, journal_file_name)

        else:

            if not experiment_name:
                logger.info("Experiment environment variable --> \"EXP\" not set quitting experiment")
            if not test_json:
                logger.info("File to pick up for chaos json --> \"FILE\" not set quitting experiment")
            if not namespace:
                logger.info("Namespace environment variable not set")
                logger.info("Namespace environment variable --> \"NAME_SPACE\" not set")
                logger.info("Please set experiment name and namespace in environment example \n"
                            "EXPERIMENT=\"experiment_name\" \n"
                            "NAME_SPACE=\"namespace\"\n"
                            "Quitting experiment")
        return test_result

    return inner


class ChaosAction(argparse.Action):
    """
    The intent of a custom action class for Chaos tests is to translate environment variable into Argsparse variable.
    If updated in actions in args parse, this will get the environment variable value and sets the same in args parse and
    at the same time will override default value and required values in args parse, if environment variables are set.

    """
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=0,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None,
                 **kwargs
                 ):
        if nargs != 0:
            raise ValueError('nargs for ChaosAction must be 0')
        var_from_dest = str(dest).upper()
        environment_from_dest = os.environ.get(var_from_dest, None)
        if environment_from_dest is None:
            logger.info("Setting environment variable %s with value %s" % (var_from_dest, default))
            os.environ.setdefault(var_from_dest, str(default))
            environment_params_for_test[var_from_dest] = str(default)
        else:
            logger.info("Environment variable value is already set for %s with value %s" % (var_from_dest,
                                                                                            environment_from_dest))
            logger.info("Setting default value for " + dest + " With value " + environment_from_dest)

            default = environment_from_dest
            logger.info("New value for " + dest + " is " + default + "  \"required\" flag if set, will be set to false "
                                                                     "since its value is updated in env variable ")
            required = False

        argparse.Action.__init__(self,
                                 option_strings=option_strings,
                                 dest=dest,
                                 nargs=nargs,
                                 const=const,
                                 default=default,
                                 type=type,
                                 choices=choices,
                                 required=required,
                                 help=help,
                                 metavar=metavar,
                                 **kwargs
                                 )

        return

    def __call__(self, parser, namespace, values,
                 option_string=None):
        var_from_dest_env_variable = str(self.dest).upper()
        environment_from_dest_env_variable = os.environ.get(var_from_dest_env_variable, None)
        if environment_from_dest_env_variable is None and values is not None:
            """
                If environment variable is not set but input args values are set, then the destination
                variable will be converted to upper_case and will set the environment variabled with default value
            """
            logger.info("Environment variable %s override with value %s " % (var_from_dest_env_variable, str(values)))
            os.environ.setdefault(var_from_dest_env_variable, str(values))
            environment_params_for_test[var_from_dest_env_variable] = str(values)
        elif environment_from_dest_env_variable and values is not None:
            """
                If environment variable is  set but input values are also set, then the environment variable will 
                be set with the value from args parse input value 
            """
            logger.info("Environment variable %s is set, override given -->  %s override with value %s "
                        % (var_from_dest_env_variable, var_from_dest_env_variable, str(values)))
            os.environ[var_from_dest_env_variable] = str(values)
            environment_params_for_test[var_from_dest_env_variable] = str(values)
        elif environment_from_dest_env_variable and values is None:
            """
                If environment variable is  set but input values are not set, then environment variable value will be 
                set to default value
            """

            logger.info("Environment variable %s is set, value not  given -->  %s override with value %s "
                        % (var_from_dest_env_variable, var_from_dest_env_variable, str(values)))
            values = environment_from_dest_env_variable

        setattr(namespace, self.dest, values)


class ChaosUtils(object):

    def run_chaos_engine(self, file, env_params: dict, report: str, report_endpoint: str, engineName) -> bool:
        """
        Runs chaos engine programmatically instead of using chaos binary
        :param file:
        :param env_params:
        :param report:
        :param report_endpoint:
        :return:
        """
        settings = ({}, os.environ.get("settings_path"))[os.environ.get("settings_path") is not None]
        has_deviated = False
        has_failed = False
        load_global_controls(settings)
        jornal_file_suffix = file
        try:
            try:
                with open(file, "r"):
                    logger.info("File exists in local")
            except FileNotFoundError:
                logger.info("File is not available in the current directory, looking inside site packages")
                location = site.getsitepackages().__getitem__(0)
                file_found = False
                for root, dirs, files in os.walk(location):
                    if file in files:
                        file_found = True
                        file = os.path.join(root, file)
                        break
                if not file_found:
                    logger.error("File " + file + " not found in site packages too, quitting")
                    raise FileNotFoundError("Chaos file is not found")
            experiment = load_experiment(
                click.format_filename(file), settings)
        except InvalidSource as x:
            logger.error(str(x))
            logger.debug(x)
            sys.exit(1)
        logger.info("chaos json file found, proceeding with test")
        journal = run_experiment(experiment, settings=settings)
        has_deviated = journal.get("deviated", False)
        has_failed = journal["status"] != "completed"
        json_file_name = "journal" + "-" + jornal_file_suffix
        with open(json_file_name, "w") as r:
            json.dump(
                journal, r, indent=2, ensure_ascii=False, default=encoder)
        r.close()
        if report == 'true':
            self.create_report(os.environ, journal, report_endpoint)
        if has_failed or has_deviated:
            logger.error("Test Failed")
            return has_failed and has_deviated
        else:
            logger.info("Test Passed")
            return True

    @staticmethod
    def create_report(env_params: dict, journal_file_name: str, report_endpoint):
        logging.info('report end point is : %s', report_endpoint)
        json_data = Report().run(env_params, journal_file_name, report_endpoint)
        logger.info("Output kubernetes in main:---")
        logging.info(json_data)
        logger.info("----End of output kubernetes in main")
