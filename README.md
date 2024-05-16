# Implementing the circuit-breaker pattern with Lambda extensions and DynamoDB

The provided code sample demonstrates how to get the circuit breaker extension written in Python 3.12 up and running.

## Circuit breaker pattern explained

Modern software systems frequently rely on remote calls to other systems across networks. When failures occur, they can cascade across multiple services causing service disruptions. One technique for mitigating this risk is the circuit breaker pattern, which can detect and isolate failures in a distributed system, as originally popularized by Michael Nygard in his book [Release It](https://www.amazon.com/Release-Design-Deploy-Production-Ready-Software/dp/1680502395). The circuit breaker pattern can help prevent cascading failures and improve overall system stability.
The pattern isolates the failing service and thus prevents cascading failures. It improves the overall responsiveness by preventing long waiting times for timeout periods. Furthermore, it also increases the fault tolerance of the system since it lets the system interact with the affected service again once it is available again.

This repository presents an example application, showing how AWS Lambda extensions integrate with Amazon DynamoDB to implement the circuit breaker pattern.

## Prerequisites

* An active AWS account
* AWS CLI 2.15.17 or later ([installation instructions here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
* AWS SAM CLI 1.116.0 or later ([installation instructions here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
* Git 2.39.3 or later ([installation instructions here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))
* Python 3.12 ([installation instructions here](https://www.python.org/downloads/release/python-3123/))

## Setup

First, we setup a virtual environment to install the  required packages:

```bash
python -m venv circuit_breaker_venv
source circuit_breaker_venv/bin/activate 
```

To prepare the services for deployment, we execute the build command. To then deploy the services, use this command specifying the AWS CLI profile (in the config file in the .aws folder) for the AWS account you want to deploy the services in:

```bash
sam build
sam deploy --guided --profile <AWSProfile>
```

Stack name (new-circuit-breaker-sam-stack) and region (us-east-1) can be taken over from the SAM config file (samconfig.toml). Select N for “Confirm changes before deploy”, Y for “Allow SAM CLI IAM role creation”, N for “Disable rollback”, Y for “MockMicroserviceAPIFunction may not have authorization defined, Is this okay?" and Y for "Save arguments to configuration file". The SAM configuration file name (samconfig.toml) and environment (default) can stay on the default values. You can deploy every subsequent local change in the code like this:

```bash
sam build && sam deploy
```

A common error when executing these commands is:

```bash
Error: Expecting value: line 1 column 1 (char 0)
```

This suggests that your AWS credentials have expired and you need to login again by specifying your AWS Access Key ID and AWS Secret Access Key:

```bash
aws configure
```

## Clean up

To delete all resources from this stack, execute the following command:

```bash
sam delete --stack-name new-circuit-breaker-sam-stack
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

