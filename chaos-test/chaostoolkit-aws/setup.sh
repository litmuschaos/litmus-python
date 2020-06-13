#!/bin/bash
account=""
role=""
EC2_INSTANCE_ID=""

usage() {
  echo "-i <Provide instance id>"
  echo "-a <Provide AWS account>"
  echo "-r <Provide arn role created>"
  echo "-z <Provide us zone name>"
  echo "-f <Provide experiment file>"
  echo "-x <Provide AZone>"

  echo "Example : -i i-08aabe53f633a2a8b -a 105398674341 -r chaosec2access -z us-west-2 -x us-west-2a -f ../chaostoolkit-aws/aws_count_describe.json" 
  exit
}

while getopts "i:a:r:z:f:x:" opt;
do
  case "$opt" in
    i) 
	EC2_INSTANCE_ID="${OPTARG}"
	;;
    a) 
	account="${OPTARG}"
	;;
    r) 
	role="${OPTARG}"
	;;
    z) 
	region="${OPTARG}"
	;;
    f) 
	file="${OPTARG}"
	;;
    x) 
	zone="${OPTARG}"
	;;
    *) usage;;
  esac
done

if [ ! -f /bin/jq ]; then 
    echo "--------------------------------------------------------------------------------"
    echo "Installing JQ..."
    echo "--------------------------------------------------------------------------------"
    wget --quiet https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 -O /bin/jq
    chmod 755 /bin/jq
fi 

    datetime=`date +'%s'`
    echo "--------------------------------------------------------------------------------"
    echo "AWS Assuming role .."
    echo "--------------------------------------------------------------------------------"

    #clean=`rm -rf ~/.aws`
    echo "Status for deleteing directory$clean"
    arn="arn:aws:iam::$account:role/$role"
    echo "arn value get for sts command -> $arn"
    res=`aws sts assume-role --role-arn $arn --role-session-name session-$datetime`
    echo "Result for sts command$?-$@"
    echo "respone from aws sts command - $res"
    export AWS_ACCESS_KEY_ID=`echo $res | jq -r .Credentials.AccessKeyId`
    export AWS_SECRET_ACCESS_KEY=`echo $res | jq -r .Credentials.SecretAccessKey`
    export AWS_SESSION_TOKEN=`echo $res | jq -r .Credentials.SessionToken`
    export AWS_REGION=$region
    export EC2_INSTANCE_ID=$EC2_INSTANCE_ID
    export EC2_AZ=$zone

    aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID}
    aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY}
    aws configure set aws_session_token ${AWS_SESSION_TOKEN}
    aws configure set region ${AWS_REGION}

    echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
    echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
    echo "AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN"
    echo "AWS_REGION=$AWS_REGION"
    echo "EC2_INSTANCE_ID=$EC2_INSTANCE_ID"
    echo "EC2_AZ=$zone"

chaos=`chaos run $file`
#chaos=`chaos run ../chaostoolkit-aws/aws_restart.json`
echo "Result of last execution - $?"