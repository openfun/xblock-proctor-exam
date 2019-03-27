Proctor Exam Xblock
=========================

Xblock restricting access to course test to Proctor Exam monitoring process.

[![CircleCI](https://circleci.com/gh/openfun/xblock-proctor-exam/tree/master.svg?style=svg)](https://circleci.com/gh/openfun/xblock-proctor-exam/tree/master)

## Installation

Install this package with `pip` using FUN package index _via_:

```bash
$ pip install --extra-index-url https://pypi.fury.io/openfun xblock-proctor-exam
```

Alternatively, if you intend to work on this project, clone this repository
first, and then make an editable installation _via_:

```bash
$ pip install -e ".[dev]"
```

## Configuration

Proctor Exam xblock relies on [Configurable LTI Consumer](https://github.com/openfun/xblock-configurable-lti-consumer)
which should also be installed in Python environment, therefore it also use its Django settings for configuration,
see [Configurable LTI Consumer documentation](https://github.com/openfun/xblock-configurable-lti-consumer/blob/master/README.md#configuration-examples).

A typical Proctor Exam LTI configuration should look like this:

```python
LTI_XBLOCK_CONFIGURATIONS = [
    {
        "shared_secret": "TestSharedSecret",
        "oauth_consumer_key": "TestOauthConsumerKey",
        "display_name": "",  # this is required to let xblock register itself in studio
        "is_launch_url_regex": False,
        "automatic_resizing": None,
        "inline_ratio": None,
        "ignore_configuration": True,
        "show_button": False,
        "pattern": ".*fun\.proctorexam\.com/lti\?id=(?P<exam_id>[0-9]+)",
        "hidden_fields": [
            "display_name",
            "description",
            "lti_id",
            "launch_target",
            "inline_height",
            "accept_grades_past_due",
            "ask_to_send_username",
            "ask_to_send_email",
            "custom_parameters",
            "has_score",
            "hide_launch",
            "modal_height",
            "modal_width",
            "weight",
            "button_text"
        ],
        "defaults": {
            "launch_target": "new_window",
            "lti_id": "proctor_exam",
        },
    }]
```

`configurable-lti-provide` also allows to set LTI OAuth credentials in LTI_XBLOCK_CONFIGURATION,
or in an other constant LTI_XBLOCK_SECRETS which then can be stored in encrypted vault.

```python
LTI_XBLOCK_SECRETS = {
    "proctor_exam": {
        "shared_secret": "TestSharedSecret",
        "oauth_consumer_key": "TestOauthConsumerKey",
    }
}
```

Or they can be set at course level in advanced settings

Add finally, `proctor_exam` to the list of advanced modules in the
"advanced settings" of a course.


Please note that the workbench included in the present repository is running a standard configuration with fake credentials. (see [config/settings.yml.dist](./config/settings.yml.dist))
