import typing


def get_icon(field_name: str) -> str:
    if field_name in ["parentIssue", "issue"]:
        return "TICKET"
    if field_name in ["assignee", "assigner"]:
        return "PERSON"
    if field_name in ["dueDate", "limitDate"]:
        return "CLOCK"
    return "DESCRIPTION"


def text_paragraph(text: str) -> typing.Dict[str, typing.Any]:
    return {
        "textParagraph": {
            "text": text,
        },
    }


def on_click(url: str) -> typing.Dict[str, typing.Any]:
    return {
        "openLink": {
            "url": url,
        },
    }


def key_value(
    top_label: str,
    content: str,
    content_multiline: bool = True,
    bottom_label: typing.Optional[str] = None,
    on_click: typing.Optional[typing.Dict[str, typing.Any]] = None,
    icon: typing.Optional[str] = None,
    button: typing.Optional[typing.Dict[str, typing.Any]] = None,
) -> typing.Dict[str, typing.Any]:
    key_value_dict = {
        "topLabel": top_label,
        "content": content,
        "contentMultiline": content_multiline,
    }
    if bottom_label:
        key_value_dict["bottomLabel"] = bottom_label
    if on_click:
        key_value_dict["onClick"] = on_click
    if icon:
        key_value_dict["icon"] = icon
    if button:
        key_value_dict["button"] = button
    return {
        "keyValue": key_value_dict,
    }


def text_button_link(text: str, url: str) -> typing.Dict[str, typing.Any]:
    return {
        "textButton": {
            "text": text,
            "onClick": on_click(url=url),
        },
    }
