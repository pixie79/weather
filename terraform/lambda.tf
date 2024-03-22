data "local_file" "lambda_handler_zip" {
  filename = "${path.root}/../package/out/my-lambda.zip"
}

# trunk-ignore(trivy/AVD-AWS-0066,checkov/CKV_AWS_50,checkov/CKV_AWS_116,checkov/CKV_AWS_117,checkov/CKV_AWS_116,checkov/CKV_AWS_173,checkov/CKV_AWS_272,semgrep/terraform.aws.security.aws-lambda-x-ray-tracing-not-active.aws-lambda-x-ray-tracing-not-active)
resource "aws_lambda_function" "weather_lambda" {
  filename                       = data.local_file.lambda_handler_zip.filename
  function_name                  = "environw_proxy"
  role                           = aws_iam_role.iam_for_lambda.arn
  handler                        = "environw_proxy.lambda_handler.handler"
  runtime                        = "python3.11"
  source_code_hash               = data.local_file.lambda_handler_zip.content_sha256
  timeout                        = 60
  reserved_concurrent_executions = 2
  environment { # trunk-ignore(semgrep/terraform.aws.security.aws-lambda-environment-unencrypted.aws-lambda-environment-unencrypted)
    variables = {
      WINDY_API_KEY              = var.windy_api_key
      LOG_LEVEL                  = var.log_level
      POWERTOOLS_LOG_LEVEL       = var.log_level
      WUNDERGROUND_STATION_ID_0  = var.wunderground_station_id_0
      WUNDERGROUND_STATION_ID_1  = var.wunderground_station_id_1
      WUNDERGROUND_STATION_KEY_0 = var.wunderground_station_key_0
      WUNDERGROUND_STATION_KEY_1 = var.wunderground_station_key_1
    }
  }

  tags = {
    Name = "weather_lambda"
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# trunk-ignore(trivy/AVD-AWS-0017,checkov/CKV_AWS_158,checkov/CKV_AWS_338,semgrep/terraform.aws.security.aws-cloudwatch-log-group-unencrypted.aws-cloudwatch-log-group-unencrypted)
resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${aws_lambda_function.weather_lambda.function_name}"
  retention_in_days = 7
}

resource "aws_iam_policy" "lambda_execution_policy" {
  name        = "lambda_execution_policy"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_execution_policy.json
}

resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_execution_policy.arn
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weather_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}
