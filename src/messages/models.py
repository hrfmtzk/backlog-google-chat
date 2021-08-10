import typing
from dataclasses import dataclass, field
from datetime import date, datetime
from distutils.util import strtobool

from events import EventType
from exceptions import UnsupportedEventType


def _maybe_null(maybe_null_str: str) -> typing.Optional[str]:
    if maybe_null_str == "null":
        return None
    return maybe_null_str


def _strtobool(bool_str: typing.Union[bool, str]) -> bool:
    if type(bool_str) == bool:
        return bool_str
    return bool(strtobool(bool_str))


def _optional_date(date_str: str) -> typing.Optional[date]:
    if not _maybe_null(date_str):
        return None
    return date(*map(int, date_str.split("-")))


@dataclass
class NulabAccount:
    nulab_id: str
    name: str
    unique_id: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            nulab_id=raw["nulabId"],
            name=raw["name"],
            unique_id=raw["uniqueId"],
        )


@dataclass
class CreatedUser:
    id: int
    name: str
    role_type: int
    nulab_account: typing.Optional[NulabAccount] = None
    mail_address: typing.Optional[str] = None
    user_id: typing.Optional[int] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            role_type=raw["roleType"],
            nulab_account=(
                NulabAccount.from_raw(raw["nulabAccount"])
                if raw.get("nulabAccount")
                else None
            ),
            mail_address=raw.get("mailAddress"),
            user_id=raw.get("userId"),
        )


@dataclass
class Assignee:
    id: int
    name: str
    role_type: int
    lang: typing.Optional[str] = None
    user_id: typing.Optional[int] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            role_type=raw["roleType"],
            lang=raw.get("lang"),
            user_id=raw.get("userId"),
        )


@dataclass
class Project:
    id: int
    project_key: str
    name: str
    archived: bool = False
    chart_enabled: bool = False
    subtasking_enabled: bool = False

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            project_key=raw["projectKey"],
            name=raw["name"],
            archived=_strtobool(raw.get("archived", "false")),
            chart_enabled=_strtobool(raw.get("chartEnabled", "false")),
            subtasking_enabled=_strtobool(
                raw.get("subtaskingEnabled", "false")
            ),
        )

    @property
    def project_display(self) -> str:
        return f"{self.name} ({self.project_key})"

    def project_link(self, base_url: str) -> str:
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/projects/{self.project_key}"


@dataclass
class IssueType:
    id: int
    name: str
    color: typing.Optional[str] = None
    display_order: typing.Optional[int] = None
    project_id: typing.Optional[int] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            color=_maybe_null(raw.get("color", "null")),
            display_order=raw.get("displayOrder"),
            project_id=raw.get("projectId"),
        )


@dataclass
class Status:
    id: int
    name: str

    @classmethod
    def from_id(cls, id: int):
        return cls(
            id=id,
            name={
                1: "未対応",
                2: "処理中",
                3: "処理済み",
                4: "完了",
            }[id],
        )

    def __str__(self) -> str:
        return self.name


@dataclass
class PullRequestStatus:
    id: int
    name: str

    @classmethod
    def from_id(cls, id: int):
        return cls(
            id=id,
            name={
                1: "Open",
                2: "Closed",
                3: "Merged",
            }[id],
        )

    def __str__(self) -> str:
        return self.name


@dataclass
class Category:
    name: str
    id: typing.Optional[int] = None
    display_order: typing.Optional[int] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            display_order=raw.get("displayOrder"),
        )


@dataclass
class Milestone:
    name: str
    description: str
    archived: bool = False
    id: typing.Optional[int] = None
    project_id: typing.Optional[int] = None
    display_order: typing.Optional[int] = None
    start_date: typing.Optional[date] = None
    release_due_date: typing.Optional[date] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            name=raw["name"],
            description=raw["description"],
            archived=_strtobool(raw["archived"]),
            id=raw.get("id"),
            project_id=raw.get("projectId"),
            display_order=raw.get("displayOrder"),
            start_date=_optional_date(raw.get("startDate", "")),
            release_due_date=_optional_date(raw.get("releaseDueDate", "")),
        )


@dataclass
class Version:
    name: str
    description: str
    archived: bool = False
    id: typing.Optional[int] = None
    project_id: typing.Optional[int] = None
    display_order: typing.Optional[int] = None
    start_date: typing.Optional[date] = None
    release_due_date: typing.Optional[date] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            name=raw["name"],
            description=raw["description"],
            archived=_strtobool(raw["archived"]),
            id=raw.get("id"),
            project_id=raw.get("projectId"),
            display_order=raw.get("displayOrder"),
            start_date=_optional_date(raw.get("startDate", "")),
            release_due_date=_optional_date(raw.get("releaseDueDate", "")),
        )


@dataclass
class Resolution:
    id: int
    name: str

    @classmethod
    def from_id(cls, id: int):
        return cls(
            id=id,
            name={
                0: "対応済み",
                1: "対応しない",
                2: "無効",
                3: "重複",
                4: "再現しない",
            }[id],
        )

    def __str__(self) -> str:
        return self.name


@dataclass
class Priority:
    id: int
    name: str

    @classmethod
    def from_id(cls, id: int):
        return cls(
            id=id,
            name={
                2: "高",
                3: "中",
                4: "低",
            }[id],
        )

    def __str__(self) -> str:
        return self.name


@dataclass
class CreateIssueContent:
    id: int
    key_id: int
    issue_type: IssueType
    summary: str
    description: str
    status: Status
    priority: typing.Optional[Priority] = None
    resolution: typing.Optional[Resolution] = None
    parent_issue_id: typing.Optional[int] = None
    start_date: typing.Optional[date] = None
    due_date: typing.Optional[date] = None
    category: typing.List[Category] = field(default_factory=list)
    milestone: typing.List[Milestone] = field(default_factory=list)
    versions: typing.List[Version] = field(default_factory=list)
    assignee: typing.Optional[Assignee] = None
    estimated_hours: typing.Optional[float] = None
    actual_hours: typing.Optional[float] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            key_id=raw["key_id"],
            issue_type=IssueType.from_raw(raw["issueType"]),
            summary=raw["summary"],
            description=raw["description"],
            status=Status.from_id(raw["status"]["id"]),
            priority=(
                Priority.from_id(raw["priority"]["id"])
                if raw["priority"] and raw["priority"]["id"]
                else None
            ),
            resolution=(
                Resolution.from_id(raw["resolution"]["id"])
                if raw["resolution"] and raw["resolution"]["id"]
                else None
            ),
            parent_issue_id=raw.get("parentIssueId"),
            start_date=_optional_date(raw["startDate"]),
            due_date=_optional_date(raw["dueDate"]),
            category=[Category.from_raw(c) for c in raw["category"]],
            milestone=[Milestone.from_raw(m) for m in raw["milestone"]],
            versions=[Version.from_raw(v) for v in raw["versions"]],
            assignee=(
                Assignee.from_raw(raw["assignee"]) if raw["assignee"] else None
            ),
            estimated_hours=raw.get("estimatedHours"),
            actual_hours=raw.get("actualHours"),
        )


@dataclass
class FieldInfo:
    name: str
    str_func: typing.Callable[[str], str] = field(default=lambda x: x)


def _from_id(field_class: typing.Any):
    def to_str(value: str) -> str:
        try:
            id = int(value)
        except ValueError:
            return value

        return str(field_class.from_id(id))

    return to_str


_field_map = {
    "issueType": FieldInfo("種別"),
    "summary": FieldInfo("件名"),
    "parentIssue": FieldInfo("親課題"),
    "description": FieldInfo("詳細"),
    "status": FieldInfo("状態", _from_id(Status)),
    "priority": FieldInfo("優先度", _from_id(Priority)),
    "milestone": FieldInfo("マイルストーン"),
    "category": FieldInfo("カテゴリー"),
    "versions": FieldInfo("発生バージョン"),
    "assignee": FieldInfo("担当者"),
    "assigner": FieldInfo("担当者"),
    "dueDate": FieldInfo("期限日"),
    "limitDate": FieldInfo("期限日"),
    "attachment": FieldInfo("添付ファイル"),
    "resolution": FieldInfo("完了理由", _from_id(Resolution)),
    "issue": FieldInfo("関連課題"),
    "pullRequestStatus": FieldInfo("Status", _from_id(PullRequestStatus)),
}


@dataclass
class Comment:
    id: int
    content: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(**raw)


@dataclass
class Change:
    field: str
    raw_field_name: str
    old_value: typing.Optional[str]
    new_value: typing.Optional[str]
    type: typing.Optional[str] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, str], status_as_pr: bool = False):
        field_name = raw["field"]
        if status_as_pr and field_name == "status":
            field_name = "pullRequestStatus"
        field_info = _field_map[field_name]

        return cls(
            field=field_info.name,
            raw_field_name=field_name,
            old_value=(
                field_info.str_func(raw["old_value"])
                if raw.get("old_value")
                else None
            ),
            new_value=(
                field_info.str_func(raw["new_value"])
                if raw.get("new_value")
                else None
            ),
            type=raw.get("type"),
        )


@dataclass
class SharedFile:
    id: int
    name: str
    size: int
    dir: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(**raw)


@dataclass
class UpdateIssueContent:
    id: int
    key_id: int
    summary: str
    description: str
    comment: typing.Optional[Comment]
    changes: typing.List[Change] = field(default_factory=list)
    shared_files: typing.List[SharedFile] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            key_id=raw["key_id"],
            summary=raw["summary"],
            description=raw["description"],
            comment=(
                Comment.from_raw(raw["comment"]) if raw["comment"] else None
            ),
            changes=[Change.from_raw(c) for c in raw["changes"]],
            shared_files=[
                SharedFile.from_raw(s) for s in raw.get("shared_files", [])
            ],
        )


@dataclass
class AddCommentContent:
    id: int
    key_id: int
    summary: str
    description: str
    comment: typing.Optional[Comment]

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            key_id=raw["key_id"],
            summary=raw["summary"],
            description=raw["description"],
            comment=Comment.from_raw(raw["comment"]),
        )


@dataclass
class DeleteIssueContent:
    id: int
    key_id: int

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            key_id=raw["key_id"],
        )


@dataclass
class CreateWikiContent:
    id: int
    name: str
    content: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            content=raw["content"],
        )


@dataclass
class UpdateWikiContent:
    id: int
    name: str
    content: str
    diff: str
    version: int

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            content=raw["content"],
            diff=raw["diff"],
            version=raw["version"],
        )


@dataclass
class DeleteWikiContent:
    id: int
    name: str
    content: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            content=raw["content"],
        )


@dataclass
class CommitSubversionContent:
    rev: int
    comment: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            rev=raw["rev"],
            comment=raw["comment"],
        )


@dataclass
class Repository:
    id: int
    name: str
    description: typing.Optional[str] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            description=raw.get("description"),
        )


@dataclass
class Revision:
    rev: str
    comment: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            rev=raw["rev"],
            comment=raw["comment"],
        )


@dataclass
class PushGitContent:
    repository: Repository
    ref: str
    change_type: str
    revision_count: int
    revision_type: str
    revisions: typing.List[Revision] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            repository=Repository.from_raw(raw["repository"]),
            ref=raw["ref"],
            change_type=raw["change_type"],
            revision_count=raw["revision_count"],
            revision_type=raw["revision_type"],
            revisions=[Revision.from_raw(r) for r in raw["revisions"]],
        )


@dataclass
class CreateGitContent:
    repository: Repository

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            repository=Repository.from_raw(raw["repository"]),
        )


@dataclass
class Link:
    id: int
    key_id: int
    title: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            key_id=raw["key_id"],
            title=raw["title"],
        )


@dataclass
class BulkUpdateIssueContent:
    tx_id: str
    link: typing.List[Link] = field(default_factory=list)
    changes: typing.List[Change] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            tx_id=raw["tx_id"],
            link=[Link.from_raw(x) for x in raw["link"]],
            changes=[Change.from_raw(c) for c in raw["changes"]],
        )


@dataclass
class User:
    id: int
    name: str
    nulab_account: typing.Optional[NulabAccount] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            name=raw["name"],
            nulab_account=(
                NulabAccount.from_raw(raw["nulabAccount"])
                if raw.get("nulabAccount")
                else None
            ),
        )


@dataclass
class JoinProjectContent:
    comment: typing.Optional[str] = None
    users: typing.List[User] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            comment=raw.get("comment"),
            users=[User.from_raw(u) for u in raw["users"]],
        )


@dataclass
class LeaveProjectContent:
    users: typing.List[User] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            users=[User.from_raw(u) for u in raw["users"]],
        )


@dataclass
class Issue:
    id: int
    key_id: int
    summary: str
    description: str

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(**raw)


@dataclass
class CreatePullRequestContent:
    id: int
    number: int
    summary: str
    description: str
    repository: Repository
    base: str
    branch: str
    comment: typing.Optional[Comment] = None
    diff: typing.Optional[str] = None
    issue: typing.Optional[Issue] = None
    assignee: typing.Optional[Assignee] = None
    changes: typing.List[Change] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            number=raw["number"],
            summary=raw["summary"],
            description=raw["description"],
            repository=Repository.from_raw(raw["repository"]),
            base=raw["base"],
            branch=raw["branch"],
            comment=(
                Comment.from_raw(raw["comment"]) if raw.get("comment") else None
            ),
            diff=raw.get("diff"),
            issue=Issue.from_raw(raw["issue"]) if raw.get("issue") else None,
            assignee=(
                Assignee.from_raw(raw["assignee"])
                if raw.get("assignee")
                else None
            ),
            changes=[
                Change.from_raw(c, status_as_pr=True) for c in raw["changes"]
            ],
        )


@dataclass
class UpdatePullRequestContent:
    id: int
    number: int
    summary: str
    description: str
    repository: Repository
    base: str
    branch: str
    comment: typing.Optional[Comment] = None
    diff: typing.Optional[str] = None
    issue: typing.Optional[Issue] = None
    assignee: typing.Optional[Assignee] = None
    changes: typing.List[Change] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            number=raw["number"],
            summary=raw["summary"],
            description=raw["description"],
            repository=Repository.from_raw(raw["repository"]),
            base=raw["base"],
            branch=raw["branch"],
            comment=(
                Comment.from_raw(raw["comment"]) if raw.get("comment") else None
            ),
            diff=raw.get("diff"),
            issue=Issue.from_raw(raw["issue"]) if raw.get("issue") else None,
            assignee=(
                Assignee.from_raw(raw["assignee"])
                if raw.get("assignee")
                else None
            ),
            changes=[
                Change.from_raw(c, status_as_pr=True) for c in raw["changes"]
            ],
        )


@dataclass
class CommentPullRequestContent:
    id: int
    number: int
    summary: str
    description: str
    repository: Repository
    base: str
    branch: str
    comment: typing.Optional[Comment] = None
    diff: typing.Optional[str] = None
    issue: typing.Optional[Issue] = None
    assignee: typing.Optional[Assignee] = None
    changes: typing.List[Change] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        return cls(
            id=raw["id"],
            number=raw["number"],
            summary=raw["summary"],
            description=raw["description"],
            repository=Repository.from_raw(raw["repository"]),
            base=raw["base"],
            branch=raw["branch"],
            comment=(
                Comment.from_raw(raw["comment"]) if raw.get("comment") else None
            ),
            diff=raw.get("diff"),
            issue=Issue.from_raw(raw["issue"]) if raw.get("issue") else None,
            assignee=(
                Assignee.from_raw(raw["assignee"])
                if raw.get("assignee")
                else None
            ),
            changes=[
                Change.from_raw(c, status_as_pr=True) for c in raw["changes"]
            ],
        )


@dataclass
class WebhookEvent:
    id: int
    type: EventType
    created: datetime
    created_user: CreatedUser
    content: typing.Union[
        CreateIssueContent,
        UpdateIssueContent,
        AddCommentContent,
        DeleteIssueContent,
        CreateWikiContent,
        UpdateWikiContent,
        DeleteWikiContent,
        CommitSubversionContent,
        PushGitContent,
        CreateGitContent,
        BulkUpdateIssueContent,
        JoinProjectContent,
        LeaveProjectContent,
        CreatePullRequestContent,
        UpdatePullRequestContent,
        CommentPullRequestContent,
    ]
    project: typing.Optional[Project] = None

    @classmethod
    def from_raw(cls, raw: typing.Dict[str, typing.Any]):
        event_type = EventType(raw["type"])
        return cls(
            id=raw["id"],
            type=event_type,
            created=datetime.fromisoformat(raw["created"][:-1] + "+00:00"),
            created_user=CreatedUser.from_raw(raw["createdUser"]),
            content=cls._content_map(event_type, raw["content"]),
            project=(
                Project.from_raw(raw["project"]) if raw.get("project") else None
            ),
        )

    @classmethod
    def _content_map(
        cls,
        event_type: EventType,
        raw_content: typing.Dict[str, typing.Any],
    ) -> typing.Union[
        CreateIssueContent,
        UpdateIssueContent,
        AddCommentContent,
        DeleteIssueContent,
        CreateWikiContent,
        UpdateWikiContent,
        DeleteWikiContent,
        CommitSubversionContent,
        PushGitContent,
        CreateGitContent,
        BulkUpdateIssueContent,
        JoinProjectContent,
        LeaveProjectContent,
        CreatePullRequestContent,
        UpdatePullRequestContent,
        CommentPullRequestContent,
    ]:
        try:
            return {
                EventType.CREATE_ISSUE: CreateIssueContent,
                EventType.UPDATE_ISSUE: UpdateIssueContent,
                EventType.ADD_COMMENT: AddCommentContent,
                EventType.DELETE_ISSUE: DeleteIssueContent,
                EventType.CREATE_WIKI: CreateWikiContent,
                EventType.UPDATE_WIKI: UpdateWikiContent,
                EventType.DELETE_WIKI: DeleteWikiContent,
                EventType.COMMIT_SUBVERSION: CommitSubversionContent,
                EventType.PUSH_GIT: PushGitContent,
                EventType.CREATE_GIT: CreateGitContent,
                EventType.BULK_UPDATE_ISSUE: BulkUpdateIssueContent,
                EventType.JOIN_PROJECT: JoinProjectContent,
                EventType.LEAVE_PROJECT: LeaveProjectContent,
                EventType.CREATE_PULL_REQUEST: CreatePullRequestContent,
                EventType.UPDATE_PULL_REQUEST: UpdatePullRequestContent,
                EventType.COMMENT_PULL_REQUEST: CommentPullRequestContent,
            }[event_type].from_raw(raw_content)
        except KeyError:
            raise UnsupportedEventType(
                f"event type `{event_type.value}` is not supported"
            )

    @property
    def issue_key(self) -> str:
        if self.type not in [
            EventType.CREATE_ISSUE,
            EventType.UPDATE_ISSUE,
            EventType.ADD_COMMENT,
            EventType.DELETE_ISSUE,
        ]:
            raise AttributeError(
                f"issue_key is not supported in type `{self.type}`"
            )
        return f"{self.project.project_key}-{self.content.key_id}"

    def issue_link(self, base_url: str) -> str:
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/view/{self.issue_key}"

    def issue_comment_link(self, base_url: str) -> str:
        if self.type not in [EventType.UPDATE_ISSUE, EventType.ADD_COMMENT]:
            raise AttributeError(
                "issue_comment_link is not supported in type `{self.type}`"
            )
        return f"{self.issue_link(base_url)}#comment-{self.content.comment.id}"

    def shared_file_link(self, base_url: str, shared_file: SharedFile) -> str:
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/ViewSharedFile.action?projectKey={self.project.project_key}&sharedFileId={shared_file.id}"  # noqa

    def wiki_link(self, base_url: str) -> str:
        if self.type not in [EventType.CREATE_WIKI, EventType.UPDATE_WIKI]:
            raise AttributeError(f"wiki_link is not supported in `{self.type}`")
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/alias/wiki/{self.content.id}"

    def wiki_diff_link(self, base_url: str) -> str:
        if self.type not in [EventType.UPDATE_WIKI]:
            raise AttributeError(f"wiki_link is not supported in `{self.type}`")
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/alias/wiki/diff/{self.content.id}/{self.content.version - 1}...{self.content.version}"  # noqa

    def subversion_commit_link(self, base_url: str) -> str:
        if self.type not in [EventType.COMMIT_SUBVERSION]:
            raise AttributeError(
                f"subversion_commit_link is not supported in `{self.type}`"
            )
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/rev/{self.project.project_key}/{self.content.rev}"

    def git_repository_link(self, base_url: str) -> str:
        if self.type not in [EventType.PUSH_GIT, EventType.CREATE_GIT]:
            raise AttributeError(
                f"git_repository_link is not supported in `{self.type}`"
            )
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/git/{self.project.project_key}/{self.content.repository.name}"  # noqa

    def git_branch_link(self, base_url: str) -> str:
        if self.type not in [EventType.PUSH_GIT]:
            raise AttributeError(
                f"git_branch_link is not supported in `{self.type}`"
            )
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/git/{self.project.project_key}/{self.content.repository.name}/tree/{self.content.ref.split('/')[-1]}"  # noqa

    def git_commit_link(self, base_url: str, revision: Revision) -> str:
        if self.type not in [EventType.PUSH_GIT]:
            raise AttributeError(
                f"git_commit_link is not supported in `{self.type}`"
            )
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/git/{self.project.project_key}/{self.content.repository.name}/commit/{revision.rev}"  # noqa

    def pull_request_link(self, base_url: str) -> str:
        if self.type not in [
            EventType.CREATE_PULL_REQUEST,
            EventType.UPDATE_PULL_REQUEST,
            EventType.COMMENT_PULL_REQUEST,
        ]:
            raise AttributeError(
                f"pull_request_link is not supported in `{self.type}`"
            )
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return f"{base_url}/git/{self.project.project_key}/{self.content.repository.name}/pullRequests/{self.content.number}"  # noqa
