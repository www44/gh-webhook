resource "time_sleep" "wait_10_seconds" {
  create_duration = "10s"
  depends_on      = [aws_api_gateway_deployment.deployment]
}

resource "github_organization_webhook" "webhook" {

  configuration {
    url          = "${aws_api_gateway_stage.github.invoke_url}${aws_api_gateway_resource.resource.path}"
    content_type = "json"
  }

  active = true

  events = ["repository"]

  depends_on = [time_sleep.wait_10_seconds]
}