variable "myregion" {
  description = "aws region"
}

variable "accountId" {
  description = "aws account id"
}

variable "githubOwner" {
  description = "target github organization"
}

variable "githubSecretName" {
  description = "aws secret name with github access token"
  default     = "githubToken"
}