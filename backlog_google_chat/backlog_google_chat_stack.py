import typing

from aws_cdk import (
    aws_apigateway as apigateway,
    aws_certificatemanager as acm,
    aws_lambda as lambda_,
    aws_lambda_python as lambda_python,
    aws_logs as logs,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    core as cdk,
)

DEFAULT_GOOGLE_CHAT_API = "https://chat.googleapis.com"


class BacklogGoogleChatStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        backlog_base_url: typing.Optional[str] = None,
        google_chat_api: typing.Optional[str] = None,
        domain_name: typing.Optional[str] = None,
        certificate_arn: typing.Optional[str] = None,
        hosted_zone_id: typing.Optional[str] = None,
        zone_name: typing.Optional[str] = None,
        log_level: typing.Optional[str] = None,
        sentry_dsn: typing.Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        log_level = log_level or "INFO"
        backlog_base_url = backlog_base_url or "https://backlog.com"
        google_chat_api = google_chat_api or DEFAULT_GOOGLE_CHAT_API

        function = lambda_python.PythonFunction(
            self,
            "Function",
            entry="src/messages",
            index="index.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            environment={
                "BACKLOG_BASE_URL": backlog_base_url,
                "GOOGLE_CHAT_API": google_chat_api,
                "LOG_LEVEL": log_level,
                "POWERTOOLS_SERVICE_NAME": "backlog-google-chat",
                "SENTRY_DSN": sentry_dsn or "",
            },
            log_retention=logs.RetentionDays.ONE_MONTH,
        )

        api = apigateway.RestApi(
            self,
            "RestApi",
        )
        message_resource = (
            api.root.add_resource("v1")
            .add_resource("spaces")
            .add_resource("{space_id}")
            .add_resource("messages")
        )
        message_resource.add_method(
            http_method="POST",
            integration=apigateway.LambdaIntegration(
                handler=function,
            ),
        )

        if domain_name and certificate_arn:
            domain_name_alias = api.add_domain_name(
                "DomainName",
                certificate=acm.Certificate.from_certificate_arn(
                    self,
                    "Certificate",
                    certificate_arn=certificate_arn,
                ),
                domain_name=domain_name,
                endpoint_type=apigateway.EndpointType.EDGE,
                security_policy=apigateway.SecurityPolicy.TLS_1_2,
            )

            cdk.CfnOutput(
                self,
                "DomainNameAliasDomainName",
                value=domain_name_alias.domain_name_alias_domain_name,
            )

            if hosted_zone_id and zone_name:
                route53.ARecord(
                    self,
                    "ARecord",
                    record_name=domain_name,
                    target=route53.RecordTarget.from_alias(
                        route53_targets.ApiGateway(api)
                    ),
                    zone=route53.HostedZone.from_hosted_zone_attributes(
                        self,
                        "HostedZone",
                        hosted_zone_id=hosted_zone_id,
                        zone_name=zone_name,
                    ),
                )
