import difflib
import os
import typing
from urllib import parse

import gchat_utils
import models
import requests
import sentry_sdk
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import ApiGatewayResolver
from aws_lambda_powertools.logging import correlation_paths
from exceptions import UnsupportedEventType
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from webhook import WebhookApp

tracer = Tracer()
logger = Logger()
app = ApiGatewayResolver()

sentry_dsn = os.environ.get("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[AwsLambdaIntegration()],
        traces_sample_rate=1.0,
    )


backlog_base_url = os.environ["BACKLOG_BASE_URL"]
if backlog_base_url.endswith("/"):
    backlog_base_url = backlog_base_url[:-1]

google_chat_api = os.environ["GOOGLE_CHAT_API"]
webhook = WebhookApp()


def text_diff(old: str, new: str) -> str:
    def ensure_newline_end(s: str) -> str:
        if not s.endswith("\n"):
            s += "\n"
        return s

    return "".join(
        difflib.unified_diff(
            ensure_newline_end(old).splitlines(keepends=True),
            ensure_newline_end(new).splitlines(keepends=True),
        )
    )


@webhook.create_issue
def create_issue():
    content: models.CreateIssueContent = webhook.event.content
    widgets = [
        gchat_utils.text_paragraph(content.description),
        gchat_utils.key_value(
            top_label="種別",
            content=content.issue_type.name,
            icon=gchat_utils.get_icon("issueType"),
        ),
    ]
    if content.assignee:
        widgets.append(
            gchat_utils.key_value(
                top_label="担当者",
                content=content.assignee.name,
                icon=gchat_utils.get_icon("assignee"),
            )
        )
    if content.priority:
        widgets.append(
            gchat_utils.key_value(
                top_label="優先度",
                content=content.priority.name,
                icon=gchat_utils.get_icon("priority"),
            )
        )
    if content.milestone:
        widgets.append(
            gchat_utils.key_value(
                top_label="マイルストーン",
                content=", ".join([ms.name for ms in content.milestone]),
                icon=gchat_utils.get_icon("milestone"),
            )
        )
    if content.category:
        widgets.append(
            gchat_utils.key_value(
                top_label="カテゴリー",
                content=", ".join([cg.name for cg in content.category]),
                icon=gchat_utils.get_icon("category"),
            )
        )
    if content.versions:
        widgets.append(
            gchat_utils.key_value(
                top_label="バージョン",
                content=", ".join([ver.name for ver in content.versions]),
                icon=gchat_utils.get_icon("version"),
            )
        )
    if content.due_date:
        widgets.append(
            gchat_utils.key_value(
                top_label="期限日",
                content=content.due_date.strftime(r"%Y-%m-%d"),
                icon=gchat_utils.get_icon("dueDate"),
            )
        )
    message = {
        "text": f"課題 {webhook.event.issue_key} を追加",
        "cards": [
            {
                "header": {
                    "title": f"{webhook.event.issue_key} {content.summary}",
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": widgets,
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="課題を開く",
                                        url=webhook.event.issue_link(
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.update_issue
def update_issue():
    content: models.UpdateIssueContent = webhook.event.content
    widgets = []
    if content.comment:
        widgets.append(
            gchat_utils.text_paragraph(content.comment.content),
        )
    for change in content.changes:
        if change.raw_field_name == "description":
            widgets.append(
                gchat_utils.key_value(
                    top_label=change.field,
                    content=text_diff(change.old_value, change.new_value),
                    icon=gchat_utils.get_icon(change.raw_field_name),
                )
            )
        else:
            widgets.append(
                gchat_utils.key_value(
                    top_label=change.field,
                    content=f"{change.old_value or '--'} > {change.new_value or '--'}",  # noqa
                    icon=gchat_utils.get_icon(change.raw_field_name),
                )
            )
    for shared_file in content.shared_files:
        widgets.append(
            gchat_utils.key_value(
                top_label="添付ファイル",
                content=shared_file.name,
                button=gchat_utils.text_button_link(
                    text="ファイルを開く",
                    url=webhook.event.shared_file_link(
                        base_url=backlog_base_url,
                        shared_file=shared_file,
                    ),
                ),
            )
        )
    message = {
        "text": f"課題 {webhook.event.issue_key} を更新",
        "cards": [
            {
                "header": {
                    "title": f"{webhook.event.issue_key} {content.summary}",
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="課題を開く",
                                        url=(
                                            webhook.event.issue_comment_link(
                                                backlog_base_url
                                            )
                                            if content.comment
                                            else webhook.event.issue_link(  # noqa
                                                backlog_base_url
                                            )
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    if widgets:
        message["cards"][0]["sections"].insert(0, {"widgets": widgets})
    return message


@webhook.add_comment
def add_comment():
    content: models.AddCommentContent = webhook.event.content
    message = {
        "text": f"課題 {webhook.event.issue_key} にコメント",
        "cards": [
            {
                "header": {
                    "title": f"{webhook.event.issue_key} {content.summary}",
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            gchat_utils.text_paragraph(content.comment.content),
                        ],
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="課題を開く",
                                        url=webhook.event.issue_comment_link(
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.delete_issue
def delete_issue():
    message = {
        "text": f"課題 {webhook.event.issue_key} を削除",
        "cards": [
            {
                "header": {
                    "title": f"{webhook.event.issue_key}",
                    "subtitle": webhook.event.created_user.name,
                },
            },
        ],
    }
    return message


@webhook.create_wiki
def create_wiki():
    content: models.CreateWikiContent = webhook.event.content
    message = {
        "text": "Wiki を追加",
        "cards": [
            {
                "header": {
                    "title": content.name,
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            gchat_utils.text_paragraph(content.content),
                        ],
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="Wiki を開く",
                                        url=webhook.event.wiki_link(
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.update_wiki
def update_wiki():
    content: models.UpdateWikiContent = webhook.event.content
    message = {
        "text": "Wiki を更新",
        "cards": [
            {
                "header": {
                    "title": content.name,
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="Wiki を開く",
                                        url=webhook.event.wiki_link(
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    if content.diff:
        message["cards"][0]["sections"][0]["widgets"][0]["buttons"].append(
            gchat_utils.text_button_link(
                text="差分を開く",
                url=webhook.event.wiki_diff_link(backlog_base_url),
            )
        )
        message["cards"][0]["sections"].insert(
            0,
            {
                "widgets": [
                    {
                        "textParagraph": {
                            "text": content.diff,
                        },
                    },
                ],
            },
        )
    return message


@webhook.delete_wiki
def delete_wiki():
    content: models.CreateWikiContent = webhook.event.content
    message = {
        "text": "Wiki を削除",
        "cards": [
            {
                "header": {
                    "title": content.name,
                    "subtitle": webhook.event.created_user.name,
                },
            },
        ],
    }
    return message


@webhook.commit_subversion
def commit_subversion():
    content: models.CommitSubversionContent = webhook.event.content
    message = {
        "text": "Subversion にコミット",
        "cards": [
            {
                "header": {
                    "title": f"r{content.rev}",
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            gchat_utils.text_paragraph(content.comment),
                        ],
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="コミットを開く",
                                        url=webhook.event.subversion_commit_link(  # noqa
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.push_git
def push_git():
    content: models.PushGitContent = webhook.event.content
    message = {
        "text": "Git リポジトリにプッシュ",
        "cards": [
            {
                "header": {
                    "title": f"{content.repository.name}/{content.ref.split('/')[-1]}",  # noqa
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            gchat_utils.key_value(
                                top_label=rev.rev[:10],
                                content=rev.comment,
                                icon="DESCRIPTION",
                                button=gchat_utils.text_button_link(
                                    text="コミットを開く",
                                    url=webhook.event.git_commit_link(
                                        backlog_base_url,
                                        rev,
                                    ),
                                ),
                            )
                            for rev in content.revisions
                        ],
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="ブランチを開く",
                                        url=webhook.event.git_branch_link(  # noqa
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.create_git
def create_git():
    content: models.CreateGitContent = webhook.event.content
    message = {
        "text": "Git リポジトリを作成",
        "cards": [
            {
                "header": {
                    "title": content.repository.name,
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="リポジトリを開く",
                                        url=webhook.event.git_repository_link(  # noqa
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    if content.repository.description:
        message["cards"][0]["sections"].insert(
            0,
            {
                "widgets": [
                    gchat_utils.text_paragraph(content.repository.description),
                ],
            },
        )
    return message


@webhook.bulk_update_issue
def bulk_update_issue():
    content: models.BulkUpdateIssueContent = webhook.event.content
    message = {
        "text": "課題をまとめて更新",
        "cards": [
            {
                "header": {
                    "title": webhook.event.project.project_display,
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            gchat_utils.key_value(
                                top_label=f"{webhook.event.project.project_key}-{link.id}",  # noqa
                                content=link.title,
                                icon="TICKET",
                                button=gchat_utils.text_button_link(
                                    text="課題を開く",
                                    url=f"{backlog_base_url}/view/{webhook.event.project.project_key}-{link.id}",  # noqa
                                ),
                            )
                            for link in content.link
                        ],
                    },
                    {
                        "widgets": [
                            gchat_utils.key_value(
                                top_label=change.field,
                                content=f"{change.old_value or '--'} > {change.new_value or '--'}",  # noqa
                                icon=gchat_utils.get_icon(
                                    change.raw_field_name
                                ),
                            )
                            for change in content.changes
                        ],
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="プロジェクトを開く",
                                        url=webhook.event.project.project_link(
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.join_project
def join_project():
    content: models.JoinProjectContent = webhook.event.content
    message = {
        "text": "メンバーを変更",
        "cards": [
            {
                "header": {
                    "title": webhook.event.project.project_display,
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            gchat_utils.key_value(
                                top_label="参加",
                                content=user.name,
                                icon="PERSON",
                            )
                            for user in content.users
                        ],
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="プロジェクトを開く",
                                        url=webhook.event.project.project_link(  # noqa
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.leave_project
def leave_project():
    content: models.JoinProjectContent = webhook.event.content
    message = {
        "text": "メンバーを変更",
        "cards": [
            {
                "header": {
                    "title": webhook.event.project.project_display,
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            gchat_utils.key_value(
                                top_label="脱退",
                                content=user.name,
                                icon="PERSON",
                            )
                            for user in content.users
                        ],
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="プロジェクトを開く",
                                        url=webhook.event.project.project_link(  # noqa
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.create_pull_request
def create_pull_request():
    content: models.CreatePullRequestContent = webhook.event.content
    project_key = webhook.event.project.project_key
    repository_name = content.repository.name
    widgets = [
        gchat_utils.text_paragraph(content.description),
    ]
    if content.assignee:
        widgets.append(
            gchat_utils.key_value(
                top_label="担当者",
                content=content.assignee.name,
                icon="PERSON",
            )
        )
    if content.issue:
        widgets.append(
            gchat_utils.key_value(
                top_label="関連課題",
                content=f"{project_key}-{content.issue.key_id} {content.issue.summary}",  # noqa
                icon="TICKET",
                button=gchat_utils.text_button_link(
                    text="課題を開く",
                    url=f"{backlog_base_url}/view/{project_key}-{content.issue.key_id}",  # noqa
                ),
            )
        )
    message = {
        "text": "プルリクエストを作成",
        "cards": [
            {
                "header": {
                    "title": f"{project_key}/{repository_name}#{content.number} {content.summary}",  # noqa
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": widgets,
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="プルリクエストを開く",
                                        url=webhook.event.pull_request_link(  # noqa
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.update_pull_request
def update_pull_request():
    content: models.UpdatePullRequestContent = webhook.event.content
    project_key = webhook.event.project.project_key
    repository_name = content.repository.name
    widgets = [
        gchat_utils.text_paragraph(content.description),
    ]
    for change in content.changes:
        if change.raw_field_name == "description":
            continue
        widgets.append(
            gchat_utils.key_value(
                top_label=change.field,
                content=f"{change.old_value or '--'} > {change.new_value or '--'}",  # noqa
                icon=gchat_utils.get_icon(change.raw_field_name),
            )
        )
    message = {
        "text": "プルリクエストを更新",
        "cards": [
            {
                "header": {
                    "title": f"{project_key}/{repository_name}#{content.number} {content.summary}",  # noqa
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": widgets,
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="プルリクエストを開く",
                                        url=webhook.event.pull_request_link(  # noqa
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    return message


@webhook.comment_pull_request
def comment_pull_request():
    content: models.CommentPullRequestContent = webhook.event.content
    project_key = webhook.event.project.project_key
    repository_name = content.repository.name
    message = {
        "text": "プルリクエストにコメント",
        "cards": [
            {
                "header": {
                    "title": f"{project_key}/{repository_name}#{content.number} {content.summary}",  # noqa
                    "subtitle": webhook.event.created_user.name,
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    gchat_utils.text_button_link(
                                        text="プルリクエストを開く",
                                        url=webhook.event.pull_request_link(  # noqa
                                            backlog_base_url
                                        ),
                                    ),
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    if content.comment:
        message["cards"][0]["sections"].insert(
            0,
            {
                "widgets": [
                    gchat_utils.text_paragraph(content.comment.content)
                ],
            },
        )
    return message


@app.post("/v1/spaces/<space_id>/messages")
@tracer.capture_method
def post_handler(space_id: str):
    logger.debug(app.current_event.json_body)
    try:
        message = webhook.handle(app.current_event.json_body)
    except UnsupportedEventType as e:
        logger.warning(e)
        return {"message": "OK"}

    url = parse.urljoin(google_chat_api, app.current_event.path)
    query = {
        key: app.current_event.query_string_parameters[key]
        for key in ["key", "token"]
    }
    url += "?" + "&".join([f"{k}={v}" for k, v in query.items()])

    response = requests.post(url=url, json=message)
    logger.debug(response.text)

    return {"message": "OK"}


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
)
@tracer.capture_lambda_handler
def lambda_handler(event, context) -> typing.Dict[str, typing.Any]:
    logger.debug(event)
    return app.resolve(event, context)
