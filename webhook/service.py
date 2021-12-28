from github import Github
from github import GithubException
import json
import sys
import os
import boto3
import base64
from botocore.exceptions import ClientError


def handler(event, context):
    """webhook handler that make default branch protected 
    and creates GitHub issue
    """

    # define output variable basic structure
    output = dict()
    output["Content-Type"] = "application/json"
    output["statusCode"] = 200

    #answer for ping event
    if event.get('hook'):
        output["body"] = {"message": 'pong'}
        return output

    github = Github(get_secret(
        os.environ['github_secret_name'],
        os.environ['aws_region'])
    )
    # protect branch
    repo = github.get_repo(event['repository']['full_name'])
    branch = repo.get_branch(os.environ['git_default_branch'])
    branch.edit_protection(True)
    
    # create issue, mentioning author in description
    username = event['sender']['login']
    repo.create_issue(title="protect branch",
                      body='@{}, main branch is protected now'.format(username))
    output["body"] = {"message": 'branch {} is protected now'.format(branch.name)}
    return output


def get_secret(secret_name, region_name) -> str:
    """ return secret as plain text out of
    AWS Secret Manager
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if 'SecretString' in get_secret_value_response:
        return get_secret_value_response['SecretString']
    else:
        return base64.b64decode(get_secret_value_response['SecretBinary'])
