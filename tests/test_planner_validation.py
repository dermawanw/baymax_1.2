import pytest
from pydantic import ValidationError

from baymax.planner import ActionPlan


@pytest.mark.parametrize(
    "payload",
    [
        {
            "action": "add_note",
            "args": {"text": "besok belajar Python"},
            "say": "Saya akan menyimpan catatan tersebut.",
        },
        {
            "action": "add_note",
            "args": {"text": "study Python tomorrow"},
            "say": "I will save that note.",
        },
        {
            "action": "start_timer",
            "args": {"seconds": 300},
            "say": "Saya akan mengatur timer.",
        },
        {
            "action": "start_timer",
            "args": {"seconds": 1},
            "say": "I will set a timer.",
        },
        {
            "action": "start_timer",
            "args": {"seconds": 86400},
            "say": "I will set a timer.",
        },
        {
            "action": "open_app",
            "args": {"name": "calculator"},
            "say": "Saya akan membuka kalkulator.",
        },
        {
            "action": "open_app",
            "args": {"name": "notepad"},
            "say": "I will open Notepad.",
        },
        {
            "action": "reply_only",
            "args": {},
            "say": "Berapa lama timer yang kamu inginkan?",
        },
    ],
)
def test_accept_valid_plan(payload):
    plan = ActionPlan.model_validate(payload)

    assert plan.action == payload["action"]


@pytest.mark.parametrize(
    "action,args",
    [
        # Catatan kosong atau tidak ada.
        ("add_note", {}),
        ("add_note", {"text": ""}),
        ("add_note", {"text": "   "}),

        # Durasi tidak valid atau belum diberikan.
        ("start_timer", {}),
        ("start_timer", {"seconds": 0}),
        ("start_timer", {"seconds": -1}),
        ("start_timer", {"seconds": 86401}),

        # Harus integer, bukan string, pecahan, atau boolean.
        ("start_timer", {"seconds": "300"}),
        ("start_timer", {"seconds": 1.5}),
        ("start_timer", {"seconds": True}),

        # Aplikasi di luar allowlist.
        ("open_app", {}),
        ("open_app", {"name": "terminal"}),
        ("open_app", {"name": "/bin/bash"}),
        ("open_app", {"name": "calculator; rm -rf /"}),

        # Argumen tidak sesuai aksi.
        ("add_note", {"text": "belajar", "seconds": 10}),
        ("start_timer", {"seconds": 10, "name": "notepad"}),
        ("open_app", {"name": "notepad", "text": "belajar"}),
        ("reply_only", {"seconds": 10}),

        # Kunci argumen yang tidak dikenal.
        ("reply_only", {"command": "echo hello"}),
    ],
)
def test_reject_invalid_arguments(action, args):
    with pytest.raises(ValidationError):
        ActionPlan.model_validate(
            {
                "action": action,
                "args": args,
                "say": "Test response.",
            }
        )


def test_reject_unknown_action():
    with pytest.raises(ValidationError):
        ActionPlan.model_validate(
            {
                "action": "run_shell",
                "args": {},
                "say": "I will run a command.",
            }
        )


def test_reject_unknown_top_level_field():
    with pytest.raises(ValidationError):
        ActionPlan.model_validate(
            {
                "action": "reply_only",
                "args": {},
                "say": "Hello.",
                "command": "echo hello",
            }
        )


@pytest.mark.parametrize("say", ["", "x" * 501])
def test_reject_invalid_response_length(say):
    with pytest.raises(ValidationError):
        ActionPlan.model_validate(
            {
                "action": "reply_only",
                "args": {},
                "say": say,
            }
        )


def test_trim_note_without_translating():
    plan = ActionPlan.model_validate(
        {
            "action": "add_note",
            "args": {"text": "  study Python tomorrow  "},
            "say": "I will save that note.",
        }
    )

    assert plan.args.text == "study Python tomorrow"


def test_normalize_app_name():
    plan = ActionPlan.model_validate(
        {
            "action": "open_app",
            "args": {"name": " Calculator "},
            "say": "I will open Calculator.",
        }
    )

    assert plan.args.name == "calculator"