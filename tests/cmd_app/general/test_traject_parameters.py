"""
Unit tests for `geoprob_pipe.cmd_app.general.traject_parameters.py`.
Tests performed for:
    - _specify_w(app_settings: ApplicationSettings)
"""

from unittest.mock import Mock

import pytest

import geoprob_pipe.cmd_app.general.traject_parameters as module


# --- _specify_w(app_settings: ApplicationSettings) ---
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
    input_value: str,
    expected_answer: str,
) -> None:
    """Test for all branches of validation and correct storage of user input."""
    # Mock input arguments
    app_settings = Mock()

    # Setup user inputs
    user_inputs = iter([input_value, "0.24"])

    # Mock assigned function calls
    prompt_mock = Mock()
    prompt_mock.execute.side_effect = lambda: next(user_inputs)

    text_mock = Mock(return_value=prompt_mock)

    monkeypatch.setattr(
        "InquirerPy.inquirer.text",
        text_mock,
    )

    # Mock called functions
    append_mock = Mock()
    monkeypatch.setattr(
        module,
        "_append_to_db",
        append_mock,
    )

    # Run tested function:
    module._specify_w(app_settings)

    # Check correct message printed
    captured = capsys.readouterr()
    assert expected_answer in captured.out

    # Check continue loop
    assert prompt_mock.execute.call_count == 2

    # Check accepted value stored correctly
    append_mock.assert_called_once_with(
        app_settings=app_settings,
        key="w",
        value=0.24,  # as a float
    )
