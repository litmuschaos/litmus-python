# -*- coding: utf-8 -*-
import time
from typing import Any, Dict, List

from chaosaws import aws_client
from chaosaws.types import AWSResponse
from chaoslib.types import Configuration, Secrets
from chaoslib.exceptions import FailedActivity

__all__ = ["describe_instances", "count_instances", "instance_state", "get_process_status"]


def describe_instances(filters: List[Dict[str, Any]],
                       configuration: Configuration = None,
                       secrets: Secrets = None) -> AWSResponse:
    """
    Describe instances following the specified filters.

    Please refer to https://bit.ly/2Sv9lmU

    for details on said filters.
    """  # noqa: E501
    client = aws_client('ec2', configuration, secrets)

    return client.describe_instances(Filters=filters)


def count_instances(filters: List[Dict[str, Any]],
                    configuration: Configuration = None,
                    secrets: Secrets = None) -> int:
    """
    Return count of instances matching the specified filters.

    Please refer to https://bit.ly/2Sv9lmU

    for details on said filters.
    """  # noqa: E501
    client = aws_client('ec2', configuration, secrets)
    result = client.describe_instances(Filters=filters)

    return len(result['Reservations'])


def count_instances_string(filters: List[Dict[str, Any]],
                           configuration: Configuration = None,
                           secrets: Secrets = None) -> str:
    """
    Return count of instances matching the specified filters.

    Please refer to https://bit.ly/2Sv9lmU

    for details on said filters.
    """  # noqa: E501

    client = aws_client('ec2', configuration, secrets)
    result = client.describe_instances(Filters=filters)
    return str(len(result['Reservations']))


def instance_state(state: str,
                   instance_ids: List[str] = None,
                   filters: List[Dict[str, Any]] = None,
                   configuration: Configuration = None,
                   secrets: Secrets = None) -> bool:
    """
    Determines if EC2 instances match desired state

    For additional filter options, please refer to the documentation found:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
    """
    client = aws_client('ec2', configuration, secrets)

    if not any([instance_ids, filters]):
        raise FailedActivity('Probe "instance_state" missing required '
                             'parameter "instance_ids" or "filters"')

    if instance_ids:
        instances = client.describe_instances(InstanceIds=instance_ids)
    else:
        instances = client.describe_instances(Filters=filters)

    for i in instances['Reservations'][0]['Instances']:
        if i['State']['Name'] != state:
            return False
    return True


def get_process_status(instance_id: str,
                                   commands: List[str],
                                   wait_time_duration_in_secs: str = None,
                                   configuration: Configuration = None,
                                   secrets: Secrets = None) -> str:
    client = aws_client("ssm", configuration, secrets)
    if instance_id is None:
        raise FailedActivity("Need to provide instance ids to invoke kill process API")
    if commands is None or len(commands) == 0:
        raise FailedActivity("Need to provide list of commands to invoke this API")
    if wait_time_duration_in_secs is None:
        wait_time_duration_in_secs = "10"

    try:
        wait_time = int(wait_time_duration_in_secs)
    except Exception:
        raise FailedActivity("Should define wait time in number though it's a string")
    command = client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands':
                commands
        },
    )

    command_id = command['Command']['CommandId']
    print("Command id is " + str(command_id))
    wait_max_retries = 3
    status = None
    print("Waiting for 3 seconds before checking command status")
    time.sleep(3)
    print("Wait time over")
    standard_output_content = None
    while True:
        if wait_max_retries == 0:
            break

        response_list = client.list_command_invocations(
            CommandId=command_id,
            Details=True
        )
        try:
            ssm_response = response_list['CommandInvocations'][0]['CommandPlugins'][0]
            status = ssm_response['StatusDetails']
            standard_output_content = ssm_response['Output']
            print("SSM response recieved ==> \n\n")
            print(standard_output_content)

            if status == "Failed":
                break
            elif status == "Success":
                print("Succeeded!")
                break
            elif status == "InProgress":
                print("Landed in In Progress gong to wait for " + wait_time_duration_in_secs + " seconds")
                time.sleep(wait_time)
                wait_max_retries -= 1
            elif status == "Pending":
                print("Landed in In pending gong to wait for " + wait_time_duration_in_secs + " seconds")
                time.sleep(wait_time)
                wait_max_retries -= 1
            elif status == "Delayed":
                print("Landed in Delayed gong to wait for " + wait_time_duration_in_secs + " seconds")
                time.sleep(wait_time)
                wait_max_retries -= 1
        except Exception:
            print("Landed in exception gong to wait for " + wait_time_duration_in_secs + " seconds")
            time.sleep(wait_time)
            wait_max_retries -= 1

    return standard_output_content
