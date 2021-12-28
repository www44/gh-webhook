terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 4.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

data "aws_secretsmanager_secret" "github_token" {
  name = var.githubSecretName
}
data "aws_secretsmanager_secret_version" "github" {
  secret_id = data.aws_secretsmanager_secret.github_token.id
}
provider "github" {
    token = data.aws_secretsmanager_secret_version.github.secret_string
    owner = var.githubOwner
}
