from unittest.mock import Mock

import pytest

import geoprob_pipe.cmd_app.general.traject_parameters as module


@pytest.mark.parametrize(
    "input_value, expected_answer",
    [
        ("", "geen w gespecificeerd"),
        ("abc", "geen decimaal getal"),
        ("1.5", "groter dan 1.0"),
        ("0", "kleiner of gelijk aan 0.0"),
        ("-1", "kleiner of gelijk aan 0.0"),
    ],
)
def test_specify_w_validations(
    monkeypatch,
    capsys,
    input_value,
    expected_answer,
) -> None:
    app_settings = Mock()

    answers = iter([input_value, "0.24"])

    prompt_mock = Mock()
    prompt_mock.execute.side_effect = lambda: next(answers)

    text_mock = Mock(return_value=prompt_mock)

    monkeypatch.setattr(
        "InquirerPy.inquirer.text",
        text_mock,
    )

    append_mock = Mock()
    monkeypatch.setattr(
        module,
        "_append_to_db",
        append_mock,
    )

    module._specify_w(app_settings)

    captured = capsys.readouterr()

    # correct respons
    assert expected_answer in captured.out

    # correct value after invalid value
    assert prompt_mock.execute.call_count == 2

    # value stored correctly
    append_mock.assert_called_once_with(
        app_settings=app_settings,
        key="w",
        value=0.24,
    )
