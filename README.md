# GitHub webhook

Service implements GitHub organization webhook in AWS for main branch protection of newly created git repositories. Information about branch protection is available in GitHub issue, where repository creator is mentioned. Service is implemented as AWS lambda function with AWS API Gateway.

## how-to use

Solution is designed for AWS and was tested on Ubuntu 20.04 as development environment, but because of platform agnostic approach, it can developed further on other platforms. There are following parts:

* prerequisites: AWS account and GitHub account.
* [webhook](./webhook): contains python AWS Lambda implementation of GitHub webhook.
* [infrastructure](./infrastructure): [terraform](https://www.terraform.io/) based configuration for AWS Lambda, AWS API Gateway, GitHub Organization.

After solution roll-out, GitHub organization will be automatically configured with GitHub webhook.

### webhook rollout

Now we can prepare terraform environment for solution rollout:

1. Please install awscli binary

   ~~~bash
   sudo apt update
   sudo apt install -y awscli
   ~~~

2. Please change directory in terminal to *infrastructure* e.g. with `cd ../infrastructure/`
3. Please install terraform according this [documentation](https://learn.hashicorp.com/tutorials/terraform/install-cli). More information about this tool can be found [here](https://www.terraform.io/intro).
4. Go to terminal and log into aws with `aws login`
5. create gitHub Token according to [documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) and put it into aws secrets with command:

    ~~~bash
    GH_TOKEN="... token value ..."
    aws secretsmanager create-secret \
        --name githubToken \
        --description "GitHub access token." \
        --secret-string $GH_TOKEN
    ~~~

6. Create GitHub organization according following [document](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/creating-a-new-organization-from-scratch), keep organization name for later.
7. Create *terraform.tfvars* file in *infrastructure* folder, more info can be found [here](https://www.terraform.io/language/values/variables#variable-definitions-tfvars-files) with following variables:
    1. aws account id as *accountId*.
    2. aws region as *myregion*.
    3. aws secret name with github access token as *githubSecretName*.
    4. GitHub organization name as *githubOwner*.
8. roll out webhook with `terraform apply` command.
9. notice webhook_url output, it shows webhook url that was added to GitHub organization, and can be used for local testing.
10. navigate to GitHub organization webhook configuration page, open Recent Deliveries, you should see there one ping request with following response:

    ~~~json
    {"Content-Type": "application/json", "statusCode": 200, "body": {"message": "pong"}}
    ~~~

### webhook verification

Now solution is rolled out and to verify it, please go to newly created GitHub organization and create new public repository, initialized with README file according this [document](https://docs.github.com/en/get-started/quickstart/create-a-repo).

When repository is created, please go to Issues section and check, whether there is new issue with name "protect branch", and also please go to repository branch settings, main branch should be protected now.

### debugging

This section can help if solution does not work as expected.

* Please verify GitHub organization webhook *Recent Deliveries*
* Please go to AWS console and verify AWS Lambda with this [payload](./webhook/event.json) and AWS API Gateway
<!-- * Contact support :) -->

### development

#### ci/cd



#### webhook

You can develop webhook python implementation locally with python-lambda or execute `terraform apply` for new version upload.

For development environment preparation, please use following snippet:

~~~bash
# cd into checked out git project with service source code
sudo apt install -y python3 python3-pip awscli
pip install virtualenv
cd webhook
virtualenv --python=python3.8 pylambda
source pylambda/bin/activate
pip install -r requirements-dev.txt
~~~

Python-lamda uses following files for zip archive generation:

* [config.yaml](./webhook/config.yaml) describes Lambda function parameters, like AWS region and function name.
* [requirements-runtime.txt](./webhook/requirements-runtime.txt) collection of python modules for function runtime.
* [service.py](./webhook/service.py) contains webhook implementation.

It is convenient to test function before roll-out, for this purpose, python-lambda provides following files:

* [event.json](./webhook/event.json) and other event files are used for GitHub event payload emulation for local testing.
* [requirements-dev.txt](./webhook/requirements-dev.txt) is used for development dependencies installation.

Framework provides also local test capability with following:

~~~bash
lambda invoke -v
# or following for non default event
lambda invoke -v --event-file event-ping.json
~~~

#### infrastructure

More information about used providers can be found here: [github](https://registry.terraform.io/providers/integrations/github/latest/docs) and [aws](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

* [api-gateway.tf](./infrastructure/api-gateway.tf) contains AWS API gateway configuration.
* [github.tf](./infrastructure/github.tf) serves for GitHub organization configuration.
* [lambda.tf](./infrastructure/lambda.tf) is used for AWS Lambda service configuration.
* [variables.tf](./infrastructure/variables.tf) defines input variables.
* [versions.tf](./infrastructure/versions.tf) configures terraform providers.
* terraform.tfvars contains variables for local usage and will not be committed in git.

## Limitations

* There is one known [bug](https://github.com/nficano/python-lambda/issues/711) in python-lambda, that prevents redeployment of AWS Lambda function. So please insert `time.sleep(10)` in pylambda/lib/python3.8/site-packages/aws_lambda/aws_lambda.py manually or with following snippet:

    ~~~bash
    sed '706i\    time.sleep(10)' pylambda/lib/python3.8/site-packages/aws_lambda/aws_lambda.py > pylambda/lib/python3.8/site-packages/aws_lambda/aws_lambda2.py
    mv pylambda/lib/python3.8/site-packages/aws_lambda/aws_lambda2.py pylambda/lib/python3.8/site-packages/aws_lambda/aws_lambda.py
    ~~~
