import json
import os

import pytest
from aws_cdk import assertions, core as cdk
from backlog_google_chat_stack import BacklogGoogleChatStack
from pytest_snapshot.plugin import Snapshot


class TestApp:
    @pytest.fixture(scope="function")
    def environ(self) -> None:
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"
        os.environ["AWS_TAGS"] = "TagKey:TagValue,AppName:backlog-google-chat"

    @pytest.fixture(scope="function")
    def app(self, environ) -> cdk.App:
        return cdk.App()

    @pytest.fixture(scope="function")
    def env(self, app: cdk.App) -> cdk.Environment:
        return cdk.Environment(
            account=app.account,
            region=app.region,
        )

    def test_backlog_google_chat_stack_snapshot(
        self, snapshot: Snapshot, app: cdk.App, env: cdk.Environment
    ) -> None:
        stack = BacklogGoogleChatStack(
            app,
            "BacklogGoogleChat",
            backlog_base_url="https://backlog.com",
            domain_name="webhook.example.com",
            certificate_arn="arn:aws:acm:us-east-1:123456789012:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  # noqa
            hosted_zone_id="xxxxxxxxxxxx",
            zone_name="example.com",
            log_level="DEBUG",
            sentry_dsn="https://xxxxxxxx.ingest.sentry.io/99999999",
        )

        snapshot.assert_match(
            json.dumps(
                assertions.Template.from_stack(stack).to_json(),
                indent=2,
            ),
            "backlog_google_chat_stack.json",
        )
