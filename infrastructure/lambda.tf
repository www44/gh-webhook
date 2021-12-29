module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "github_webhook"
  description   = "GitHub webhook"
  handler       = "service.handler"
  runtime       = "python3.8"

  source_path = [
    {
      path             = "../webhook",
      pip_requirements = "../webhook/requirements-runtime.txt",
      patterns = [
        "service.py",
        "!pylambda/.*",
        "!dist/.*",
        "!event.*.json",
        "!requirements.*",
        "!config.yaml",
        "!.gitignore",
        "!__pycache__/.*"
      ]
    }
  ]
  environment_variables = {
    "github_secret_name" = var.githubSecretName,
    "aws_region"         = var.myregion,
    "git_default_branch" = "main"
  }

  publish       = true
  attach_policy = true
  policy        = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"

  allowed_triggers = {
    APIGateway = {
      service    = "apigateway"
      source_arn = "arn:aws:execute-api:${var.myregion}:${var.accountId}:${aws_api_gateway_rest_api.webhook.id}/*/*${aws_api_gateway_resource.resource.path}"
    }
  }

  tags = {
    Name = "webhook"
  }
}
