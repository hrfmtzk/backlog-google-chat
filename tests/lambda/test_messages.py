import json
import os
import sys
import typing
from dataclasses import dataclass
from pathlib import Path

import pytest
from moto import mock_cloudwatch
from pytest_mock import MockerFixture


@dataclass
class LambdaContext:
    function_name: str = "test"
    memory_limit_in_mb: int = 128
    invoked_function_arn: str = (
        "arn:aws:lambda:eu-west-1:809313241:function:test"
    )
    aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"


class TestHandler:
    @pytest.fixture
    def env(self):
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"
        os.environ["GOOGLE_CHAT_API"] = "https://api.example.com"
        os.environ["BACKLOG_BASE_URL"] = "https://backlog.com"
        os.environ["POWERTOOLS_TRACE_DISABLED"] = "true"

    @pytest.fixture
    def target(self, env):
        root_dir = Path(__file__).resolve().parents[2]

        original_path = sys.path
        original_modules = sys.modules
        sys.path.append(str(root_dir / "src" / "messages"))
        from index import lambda_handler

        with mock_cloudwatch():
            yield lambda_handler

        sys.path = original_path
        sys.modules = original_modules

    @pytest.fixture
    def lambda_context(self) -> LambdaContext:
        return LambdaContext()

    def _lambda_event_wrapper(
        self,
        backlog_event: typing.Dict[str, typing.Any],
        webhook_key: str,
        webhook_token: str,
        space_id: str,
    ) -> typing.Dict[str, typing.Any]:
        return {
            "resource": "/v1/spaces/{space_id}/messages",
            "path": f"/v1/spaces/{space_id}/messages",
            "httpMethod": "POST",
            "headers": {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "cookie": "s_fid=7AAB6XMPLAFD9BBF-0643XMPL09956DE2; regStatus=pre-register",  # noqa
                "Host": "70ixmpl4fl.execute-api.us-east-2.amazonaws.com",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "upgrade-insecure-requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",  # noqa
                "X-Amzn-Trace-Id": "Root=1-5e66d96f-7491f09xmpl79d18acf3d050",
                "X-Forwarded-For": "52.255.255.12",
                "X-Forwarded-Port": "443",
                "X-Forwarded-Proto": "https",
            },
            "multiValueHeaders": {
                "accept": [
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"  # noqa
                ],
                "accept-encoding": ["gzip, deflate, br"],
                "accept-language": ["en-US,en;q=0.9"],
                "cookie": [
                    "s_fid=7AABXMPL1AFD9BBF-0643XMPL09956DE2; regStatus=pre-register;"  # noqa
                ],
                "Host": ["70ixmpl4fl.execute-api.ca-central-1.amazonaws.com"],
                "sec-fetch-dest": ["document"],
                "sec-fetch-mode": ["navigate"],
                "sec-fetch-site": ["none"],
                "upgrade-insecure-requests": ["1"],
                "User-Agent": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"  # noqa
                ],
                "X-Amzn-Trace-Id": ["Root=1-5e66d96f-7491f09xmpl79d18acf3d050"],
                "X-Forwarded-For": ["52.255.255.12"],
                "X-Forwarded-Port": ["443"],
                "X-Forwarded-Proto": ["https"],
            },
            "queryStringParameters": {
                "key": webhook_key,
                "token": webhook_token,
            },
            "multiValueQueryStringParameters": {
                "key": [
                    webhook_key,
                ],
                "token": [
                    webhook_token,
                ],
            },
            "pathParameters": {"space_id": space_id},
            "stageVariables": None,
            "requestContext": {
                "resourceId": "2gxmpl",
                "resourcePath": f"/v1/spaces/{space_id}/messages",
                "httpMethod": "POST",
                "extendedRequestId": "JJbxmplHYosFVYQ=",
                "requestTime": "10/Mar/2020:00:03:59 +0000",
                "path": f"/v1/spaces/{space_id}/messages",
                "accountId": "123456789012",
                "protocol": "HTTP/1.1",
                "stage": "Prod",
                "domainPrefix": "70ixmpl4fl",
                "requestTimeEpoch": 1583798639428,
                "requestId": "77375676-xmpl-4b79-853a-f982474efe18",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": None,
                    "cognitoIdentityId": None,
                    "caller": None,
                    "sourceIp": "52.255.255.12",
                    "principalOrgId": None,
                    "accessKey": None,
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": None,
                    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",  # noqa
                    "user": None,
                },
                "domainName": "70ixmpl4fl.execute-api.us-east-2.amazonaws.com",
                "apiId": "70ixmpl4fl",
            },
            "body": json.dumps(backlog_event),
            "isBase64Encoded": False,
        }

    def assert_response(
        self,
        response: typing.Dict[str, typing.Any],
        status_code: int,
        body: typing.Dict[str, typing.Any],
    ) -> None:
        assert response["statusCode"] == status_code
        assert json.loads(response["body"]) == body

    def test_create_issue(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T11:02:22Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 1,
            "content": {
                "summary": "test issue",
                "key_id": 100,
                "customFields": [],
                "dueDate": "2017-07-19",
                "description": "test description",
                "priority": {
                    "name": "",
                    "id": None,
                },
                "resolution": {
                    "name": "",
                    "id": None,
                },
                "actualHours": None,
                "issueType": {
                    "color": "null",
                    "name": "Bug",
                    "displayOrder": None,
                    "id": 400,
                    "projectId": None,
                },
                "milestone": [
                    {
                        "archived": "false",
                        "releaseDueDate": "null",
                        "name": "prototype release",
                        "displayOrder": None,
                        "description": "",
                        "id": None,
                        "projectId": None,
                        "startDate": "null",
                    }
                ],
                "versions": [
                    {
                        "archived": "false",
                        "releaseDueDate": "null",
                        "name": "Version0.1",
                        "displayOrder": None,
                        "description": "",
                        "id": None,
                        "projectId": None,
                        "startDate": "null",
                    }
                ],
                "parentIssueId": None,
                "estimatedHours": None,
                "id": 100,
                "assignee": None,
                "category": [
                    {
                        "name": "Category1",
                        "displayOrder": None,
                        "id": None,
                    },
                    {
                        "name": "Category2",
                        "displayOrder": None,
                        "id": None,
                    },
                ],
                "startDate": "",
                "status": {"name": "In Progress", "id": 2},
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "課題 TEST-100 を追加",
            "cards": [
                {
                    "header": {
                        "title": "TEST-100 test issue",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "test description",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "種別",
                                        "content": "Bug",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "マイルストーン",
                                        "content": "prototype release",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "カテゴリー",
                                        "content": "Category1, Category2",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "バージョン",
                                        "content": "Version0.1",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "期限日",
                                        "content": "2017-07-19",
                                        "contentMultiline": True,
                                        "icon": "CLOCK",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "課題を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/view/TEST-100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_update_issue(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T11:45:58Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 2,
            "content": {
                "summary": "test issue",
                "key_id": 100,
                "changes": [
                    {
                        "field": "priority",
                        "old_value": "",
                        "type": "standard",
                        "new_value": "",
                    },
                    {
                        "field": "status",
                        "old_value": "1",
                        "new_value": "2",
                    },
                    {
                        "field": "description",
                        "old_value": "old statement",
                        "new_value": "new statement",
                    },
                ],
                "description": "test description",
                "comment": {
                    "id": 200,
                    "content": "test comment",
                },
                "id": 100,
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "課題 TEST-100 を更新",
            "cards": [
                {
                    "header": {
                        "title": "TEST-100 test issue",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "test comment",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "優先度",
                                        "content": "-- > --",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "状態",
                                        "content": "未対応 > 処理中",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "詳細",
                                        "content": "\n".join(
                                            [
                                                "--- ",
                                                "+++ ",
                                                "@@ -1 +1 @@",
                                                "-old statement",
                                                "+new statement",
                                                "",
                                            ]
                                        ),
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "課題を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/view/TEST-100#comment-200",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_update_issue_with_shared_files(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T11:45:58Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 2,
            "content": {
                "summary": "test issue",
                "key_id": 100,
                "changes": [],
                "description": "test description",
                "shared_files": [
                    {
                        "size": 100,
                        "name": "test.png",
                        "id": 999,
                        "dir": "/test",
                    }
                ],
                "comment": None,
                "id": 100,
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "課題 TEST-100 を更新",
            "cards": [
                {
                    "header": {
                        "title": "TEST-100 test issue",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "keyValue": {
                                        "topLabel": "添付ファイル",
                                        "content": "test.png",
                                        "contentMultiline": True,
                                        "button": {
                                            "textButton": {
                                                "text": "ファイルを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/ViewSharedFile.action?projectKey=TEST&sharedFileId=999",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "課題を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/view/TEST-100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_add_comment(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T11:50:16Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 3,
            "content": {
                "summary": "test issue",
                "key_id": 100,
                "description": "test description",
                "comment": {
                    "id": 200,
                    "content": "test comment",
                },
                "id": 100,
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "課題 TEST-100 にコメント",
            "cards": [
                {
                    "header": {
                        "title": "TEST-100 test issue",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "test comment",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "課題を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/view/TEST-100#comment-200",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_delete_issue(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T11:55:35Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 4,
            "content": {
                "key_id": 100,
                "id": 100,
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "課題 TEST-100 を削除",
            "cards": [
                {
                    "header": {
                        "title": "TEST-100",
                        "subtitle": "John Doe",
                    },
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_create_wiki(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T12:00:42Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 5,
            "content": {
                "name": "test wiki",
                "id": 100,
                "content": "test content",
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "Wiki を追加",
            "cards": [
                {
                    "header": {
                        "title": "test wiki",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "test content",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "Wiki を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/alias/wiki/100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_update_wiki(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T12:02:57Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 6,
            "content": {
                "name": "test wiki",
                "diff": "1c1\n<test content---\n>test",
                "id": 100,
                "version": 3,
                "content": "test content",
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "Wiki を更新",
            "cards": [
                {
                    "header": {
                        "title": "test wiki",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "1c1\n<test content---\n>test",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "Wiki を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/alias/wiki/100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                        {
                                            "textButton": {
                                                "text": "差分を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/alias/wiki/diff/100/2...3",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_delete_wiki(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T12:05:24Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 7,
            "content": {
                "name": "test wiki",
                "id": 100,
                "content": "test content",
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "Wiki を削除",
            "cards": [
                {
                    "header": {
                        "title": "test wiki",
                        "subtitle": "John Doe",
                    },
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_commit_subversion(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "created": "2017-07-19T12:07:35Z",
            "project": {
                "archived": False,
                "projectKey": "TEST",
                "name": "TestProject",
                "chartEnabled": False,
                "id": 100,
                "subtaskingEnabled": False,
            },
            "id": 10,
            "type": 11,
            "content": {
                "rev": 100,
                "comment": "test commit",
            },
            "notifications": [],
            "createdUser": {
                "nulabAccount": None,
                "name": "John Doe",
                "mailAddress": None,
                "id": 103640,
                "roleType": 1,
                "userId": None,
            },
        }
        expected_chat_message = {
            "text": "Subversion にコミット",
            "cards": [
                {
                    "header": {
                        "title": "r100",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "test commit",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "コミットを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/rev/TEST/100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_push_git(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "project": {
                "archived": False,
                "name": "TestProject",
                "chartEnabled": False,
                "subtaskingEnabled": False,
                "id": 100,
                "projectKey": "TEST",
            },
            "created": "2017-07-20T16:10:04Z",
            "content": {
                "revision_count": 1,
                "change_type": "update",
                "repository": {
                    "name": "app",
                    "id": 3,
                },
                "revision_type": "commit",
                "ref": "refs/heads/test",
                "revisions": [
                    {
                        "comment": "test",
                        "rev": "e1cf1103242ea1ce59382ac2e2ab4de43751524d",
                    }
                ],
            },
            "notifications": [],
            "createdUser": {
                "roleType": 1,
                "name": "John Doe",
                "userId": None,
                "nulabAccount": None,
                "mailAddress": None,
                "id": 103640,
            },
            "type": 12,
            "id": 10,
        }
        expected_chat_message = {
            "text": "Git リポジトリにプッシュ",
            "cards": [
                {
                    "header": {
                        "title": "app/test",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "keyValue": {
                                        "topLabel": "e1cf110324",
                                        "content": "test",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                        "button": {
                                            "textButton": {
                                                "text": "コミットを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/git/TEST/app/commit/e1cf1103242ea1ce59382ac2e2ab4de43751524d",  # noqa
                                                    }
                                                },
                                            }
                                        },
                                    }
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "ブランチを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/git/TEST/app/tree/test",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_create_git(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "project": {
                "archived": False,
                "name": "TestProject",
                "chartEnabled": False,
                "subtaskingEnabled": False,
                "id": 100,
                "projectKey": "TEST",
            },
            "created": "2017-07-20T16:10:09Z",
            "content": {
                "repository": {
                    "description": "description",
                    "id": 100,
                    "name": "test",
                },
            },
            "notifications": [],
            "createdUser": {
                "roleType": 1,
                "name": "John Doe",
                "userId": None,
                "nulabAccount": None,
                "mailAddress": None,
                "id": 103640,
            },
            "type": 13,
            "id": 10,
        }
        expected_chat_message = {
            "text": "Git リポジトリを作成",
            "cards": [
                {
                    "header": {
                        "title": "test",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "description",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "リポジトリを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/git/TEST/test",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_bulk_update_issue(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "project": {
                "archived": False,
                "name": "TestProject",
                "chartEnabled": False,
                "subtaskingEnabled": False,
                "id": 100,
                "projectKey": "TEST",
            },
            "created": "2017-07-20T16:09:19Z",
            "content": {
                "link": [
                    {
                        "key_id": "100",
                        "id": "100",
                        "title": "test issue1",
                    },
                    {
                        "key_id": "101",
                        "id": "101",
                        "title": "test issue2",
                    },
                ],
                "changes": [
                    {
                        "field": "priority",
                        "type": "standard",
                        "new_value": "高",
                    }
                ],
                "tx_id": "200",
            },
            "notifications": [],
            "createdUser": {
                "roleType": 1,
                "name": "John Doe",
                "userId": None,
                "nulabAccount": None,
                "mailAddress": None,
                "id": 103640,
            },
            "type": 14,
            "id": 10,
        }
        expected_chat_message = {
            "text": "課題をまとめて更新",
            "cards": [
                {
                    "header": {
                        "title": "TestProject (TEST)",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "keyValue": {
                                        "topLabel": "TEST-100",
                                        "content": "test issue1",
                                        "contentMultiline": True,
                                        "icon": "TICKET",
                                        "button": {
                                            "textButton": {
                                                "text": "課題を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/view/TEST-100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "TEST-101",
                                        "content": "test issue2",
                                        "contentMultiline": True,
                                        "icon": "TICKET",
                                        "button": {
                                            "textButton": {
                                                "text": "課題を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/view/TEST-101",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "keyValue": {
                                        "topLabel": "優先度",
                                        "content": "-- > 高",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "プロジェクトを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/projects/TEST",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_join_project(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "project": {
                "archived": False,
                "name": "TestProject",
                "chartEnabled": False,
                "subtaskingEnabled": False,
                "id": 100,
                "projectKey": "TEST",
            },
            "created": "2017-07-20T16:10:13Z",
            "content": {
                "comment": "",
                "users": [
                    {
                        "id": 100,
                        "name": "test user",
                        "nulabAccount": {
                            "nulabId": "snGjFs8agNSJeI4ZdeiVXsTiKJd0jPJAoD60apGa0VS8RPspt4",  # noqa
                            "name": "matsu ( Yusuke Matsuura )",
                            "uniqueId": "matsuzj",
                        },
                    }
                ],
            },
            "notifications": [],
            "createdUser": {
                "roleType": 1,
                "name": "John Doe",
                "userId": None,
                "nulabAccount": None,
                "mailAddress": None,
                "id": 103640,
            },
            "type": 15,
            "id": 10,
        }
        expected_chat_message = {
            "text": "メンバーを変更",
            "cards": [
                {
                    "header": {
                        "title": "TestProject (TEST)",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "keyValue": {
                                        "topLabel": "参加",
                                        "content": "test user",
                                        "contentMultiline": True,
                                        "icon": "PERSON",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "プロジェクトを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/projects/TEST",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_leave_project(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "project": {
                "archived": False,
                "name": "TestProject",
                "chartEnabled": False,
                "subtaskingEnabled": False,
                "id": 100,
                "projectKey": "TEST",
            },
            "created": "2017-07-20T16:10:18Z",
            "content": {
                "users": [
                    {
                        "id": 100,
                        "name": "test user",
                        "nulabAccount": {
                            "nulabId": "snGjFs8agNSJeI4ZdeiVXsTiKJd0jPJAoD60apGa0VS8RPspt4",  # noqa
                            "name": "matsu ( Yusuke Matsuura )",
                            "uniqueId": "matsuzj",
                        },
                    }
                ],
            },
            "notifications": [],
            "createdUser": {
                "roleType": 1,
                "name": "John Doe",
                "userId": None,
                "nulabAccount": None,
                "mailAddress": None,
                "id": 103640,
            },
            "type": 16,
            "id": 10,
        }
        expected_chat_message = {
            "text": "メンバーを変更",
            "cards": [
                {
                    "header": {
                        "title": "TestProject (TEST)",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "keyValue": {
                                        "topLabel": "脱退",
                                        "content": "test user",
                                        "contentMultiline": True,
                                        "icon": "PERSON",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "プロジェクトを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/projects/TEST",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_create_pull_request(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "project": {
                "archived": False,
                "name": "TestProject",
                "chartEnabled": False,
                "subtaskingEnabled": False,
                "id": 100,
                "projectKey": "TEST",
            },
            "created": "2017-07-20T16:10:23Z",
            "content": {
                "comment": None,
                "description": "test description",
                "repository": {
                    "description": "test description",
                    "id": 100,
                    "name": "test-repository",
                },
                "changes": [],
                "number": 100,
                "summary": "test pull request",
                "assignee": {
                    "name": "test",
                    "id": 100000,
                    "roleType": 1,
                    "lang": None,
                    "userId": "test",
                },
                "base": "master",
                "branch": "feature",
                "diff": None,
                "issue": {
                    "summary": "summary",
                    "key_id": 100,
                    "description": "description",
                    "id": 100000,
                },
                "id": 100,
            },
            "notifications": [],
            "createdUser": {
                "roleType": 1,
                "name": "John Doe",
                "userId": None,
                "nulabAccount": None,
                "mailAddress": None,
                "id": 103640,
            },
            "type": 18,
            "id": 10,
        }
        expected_chat_message = {
            "text": "プルリクエストを作成",
            "cards": [
                {
                    "header": {
                        "title": "TEST/test-repository#100 test pull request",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "test description",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "担当者",
                                        "content": "test",
                                        "contentMultiline": True,
                                        "icon": "PERSON",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "関連課題",
                                        "content": "TEST-100 summary",
                                        "contentMultiline": True,
                                        "icon": "TICKET",
                                        "button": {
                                            "textButton": {
                                                "text": "課題を開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/view/TEST-100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "プルリクエストを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/git/TEST/test-repository/pullRequests/100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_update_pull_request(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "project": {
                "archived": False,
                "name": "TestProject",
                "chartEnabled": False,
                "subtaskingEnabled": False,
                "id": 100,
                "projectKey": "TEST",
            },
            "created": "2017-07-20T16:10:27Z",
            "content": {
                "comment": None,
                "description": "test description",
                "repository": {
                    "description": "test description",
                    "id": 100,
                    "name": "test-repository",
                },
                "changes": [
                    {
                        "field": "description",
                        "old_value": "descriptions",
                        "new_value": "descriptions\nadd",
                    },
                    {
                        "field": "assigner",
                        "old_value": "John Doe",
                        "new_value": "Jane Doe",
                    },
                    {
                        "field": "issue",
                        "old_value": "TEST-10",
                        "new_value": "",
                    },
                    {
                        "field": "status",
                        "old_value": "1",
                        "new_value": "2",
                    },
                ],
                "number": 100,
                "summary": "test pull request",
                "assignee": None,
                "base": "master",
                "branch": "feature",
                "diff": "1c1\n<test description---\n>test",
                "issue": None,
                "id": 100,
            },
            "notifications": [],
            "createdUser": {
                "roleType": 1,
                "name": "John Doe",
                "userId": None,
                "nulabAccount": None,
                "mailAddress": None,
                "id": 103640,
            },
            "type": 19,
            "id": 10,
        }
        expected_chat_message = {
            "text": "プルリクエストを更新",
            "cards": [
                {
                    "header": {
                        "title": "TEST/test-repository#100 test pull request",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "test description",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "担当者",
                                        "content": "John Doe > Jane Doe",
                                        "contentMultiline": True,
                                        "icon": "PERSON",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "関連課題",
                                        "content": "TEST-10 > --",
                                        "contentMultiline": True,
                                        "icon": "TICKET",
                                    },
                                },
                                {
                                    "keyValue": {
                                        "topLabel": "Status",
                                        "content": "Open > Closed",
                                        "contentMultiline": True,
                                        "icon": "DESCRIPTION",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "プルリクエストを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/git/TEST/test-repository/pullRequests/100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})

    def test_comment_pull_request(
        self,
        mocker: MockerFixture,
        target: typing.Callable[
            [typing.Dict[str, typing.Any], LambdaContext],
            typing.Dict[str, typing.Any],
        ],
        lambda_context: LambdaContext,
    ) -> None:
        backlog_event = {
            "project": {
                "archived": False,
                "name": "TestProject",
                "chartEnabled": False,
                "subtaskingEnabled": False,
                "id": 100,
                "projectKey": "TEST",
            },
            "created": "2017-07-20T16:10:32Z",
            "content": {
                "comment": {
                    "content": "test comment",
                    "id": 100,
                },
                "description": "test description",
                "repository": {
                    "description": "test description",
                    "id": 100,
                    "name": "test-repository",
                },
                "changes": [],
                "number": 100,
                "summary": "test pull request",
                "assignee": None,
                "base": "master",
                "branch": "feature",
                "diff": None,
                "issue": None,
                "id": 100,
            },
            "notifications": [],
            "createdUser": {
                "roleType": 1,
                "name": "John Doe",
                "userId": None,
                "nulabAccount": None,
                "mailAddress": None,
                "id": 103640,
            },
            "type": 20,
            "id": 10,
        }
        expected_chat_message = {
            "text": "プルリクエストにコメント",
            "cards": [
                {
                    "header": {
                        "title": "TEST/test-repository#100 test pull request",
                        "subtitle": "John Doe",
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "test comment",
                                    },
                                },
                            ],
                        },
                        {
                            "widgets": [
                                {
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "プルリクエストを開く",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://backlog.com/git/TEST/test-repository/pullRequests/100",  # noqa
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        lambda_event = self._lambda_event_wrapper(
            backlog_event=backlog_event,
            webhook_key="foo",
            webhook_token="bar",
            space_id="xxxx",
        )

        mocked_requests = mocker.patch("index.requests")
        response = target(lambda_event, lambda_context)
        mocked_requests.post.assert_called_once_with(
            url="https://api.example.com/v1/spaces/xxxx/messages?key=foo&token=bar",  # noqa
            json=expected_chat_message,
        )

        self.assert_response(response, 200, {"message": "OK"})
