#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from dotenv import find_dotenv, load_dotenv

from backlog_google_chat.backlog_google_chat_stack import BacklogGoogleChatStack

load_dotenv(find_dotenv())


app = cdk.App()
BacklogGoogleChatStack(
    app,
    "BacklogGoogleChatStack",
    backlog_base_url=os.environ["BACKLOG_BASE_URL"],
    domain_name=os.getenv("DOMAIN_NAME"),
    certificate_arn=os.getenv("CERTIFICATE_ARN"),
    hosted_zone_id=os.getenv("HOSTED_ZONE_ID"),
    zone_name=os.getenv("ZONE_NAME"),
    log_level=os.getenv("LOG_LEVEL"),
    sentry_dsn=os.getenv("SENTRY_DSN"),
    env=cdk.Environment(
        account=app.account,
        region=app.region,
    ),
)

app.synth()
