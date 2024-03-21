# -*- coding: utf-8 -*-
"""AWS Lambda function module for processing S3 events.

This module defines a Lambda function for handling S3 event triggers.
It utilizes utilities from aws_lambda_powertools and a custom process_records function.
"""

from aws_lambda_powertools import Logger, Tracer  # trunk-ignore(pyright/reportMissingImports)
from aws_lambda_powertools.utilities.data_classes import (  # trunk-ignore(pyright/reportMissingImports)
    APIGatewayProxyEvent,
    event_source,
)

# trunk-ignore(pyright/reportMissingImports)
from aws_lambda_powertools.utilities.typing import LambdaContext

from environw_proxy.process import process_records

tracer: Tracer = Tracer(service="weather-proxy")
logger: Logger = Logger(service="weather-proxy", utc=True, child=False)


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@event_source(data_class=APIGatewayProxyEvent)
def handler(event: APIGatewayProxyEvent, context: LambdaContext) -> bool: # trunk-ignore(pylint/W0613)
    """Handle an incoming API Gw event by processing records.

    Args:
        event (APIGatewayProxyEvent): The API Gw event triggering the lambda.
        context (LambdaContext): The context in which the lambda is running.

    Returns:
        bool: True if the process completes successfully.
    """
    if 'weather' in event.path and event.http_method == 'POST':
        return process_records(event=event.json_body)

    return False
