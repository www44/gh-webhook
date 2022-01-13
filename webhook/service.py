"""
Python implementation of GitHub webhook for protecting main branch
"""

import os
import base64
import boto3
from github import Github


def handler(event, context):
    """
    webhook handler that make default branch protected
    and creates GitHub issue.

    Parameters
    -----------
    event: dict
        GitHub webhook payload
    context: dict
        This object provides methods and properties that provide
        information about the invocation, function, and execution
        environment.

    Returns
    -------
    output: dict
        Information about execution result.
        Pong - for ping command
        Branch status update summary or error messages.
    """

    # define output variable structure
    output = {}
    output["Content-Type"] = "application/json"
    output["statusCode"] = 200

    # answer for ping event
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
                      body=f"@{username}, main branch is under protection.")
    output["body"] = {"message": f"branch {branch.name} is under protection."}
    return output


def get_secret(secret_name, region_name) -> str:
    """
    Get secret out of AWS Secret Manager

    Parameters
    ----------
    secret_name: str
        Name of AWS secret to obtain
    region_name: str
        Name of AWS region, where secret is stored

    Returns
    -------
    secret as plain text: str
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if 'SecretString' in get_secret_value_response:
        return get_secret_value_response['SecretString']
    return base64.b64decode(get_secret_value_response['SecretBinary'])
