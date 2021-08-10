import typing

from models import WebhookEvent

from events import EventType


class WebhookApp:
    def __init__(self) -> None:
        self._event_handlers: typing.Dict[str, typing.Callable] = {}

    def handle(self, event: typing.Dict[str, typing.Any]) -> typing.Any:
        webhook_event = WebhookEvent.from_raw(event)
        self.event = webhook_event
        return self._event_handlers[webhook_event.type]()

    @property
    def create_issue(self):
        return self._event(EventType.CREATE_ISSUE)

    @property
    def update_issue(self):
        return self._event(EventType.UPDATE_ISSUE)

    @property
    def add_comment(self):
        return self._event(EventType.ADD_COMMENT)

    @property
    def delete_issue(self):
        return self._event(EventType.DELETE_ISSUE)

    @property
    def create_wiki(self):
        return self._event(EventType.CREATE_WIKI)

    @property
    def update_wiki(self):
        return self._event(EventType.UPDATE_WIKI)

    @property
    def delete_wiki(self):
        return self._event(EventType.DELETE_WIKI)

    @property
    def commit_subversion(self):
        return self._event(EventType.COMMIT_SUBVERSION)

    @property
    def push_git(self):
        return self._event(EventType.PUSH_GIT)

    @property
    def create_git(self):
        return self._event(EventType.CREATE_GIT)

    @property
    def bulk_update_issue(self):
        return self._event(EventType.BULK_UPDATE_ISSUE)

    @property
    def join_project(self):
        return self._event(EventType.JOIN_PROJECT)

    @property
    def leave_project(self):
        return self._event(EventType.LEAVE_PROJECT)

    @property
    def create_pull_request(self):
        return self._event(EventType.CREATE_PULL_REQUEST)

    @property
    def update_pull_request(self):
        return self._event(EventType.UPDATE_PULL_REQUEST)

    @property
    def comment_pull_request(self):
        return self._event(EventType.COMMENT_PULL_REQUEST)

    def _event(self, event_type: EventType):
        def register_handler(func: typing.Callable) -> typing.Callable:
            self._event_handlers[event_type] = func
            return func

        return register_handler
