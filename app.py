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
    log_level=os.getenv("LOG_LEVEL"),
    sentry_dsn=os.getenv("SENTRY_DSN"),
    env=cdk.Environment(
        account=app.account,
        region=app.region,
    ),
)

app.synth()
