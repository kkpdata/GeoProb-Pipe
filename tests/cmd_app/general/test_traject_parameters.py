from unittest.mock import Mock

import pytest

from geoprob_pipe.cmd_app.general.traject_parameters import _specify_w


@pytest.mark.parametrize(
    "input_value, verwachte_tekst",
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
    verwachte_tekst,
):
    app_settings = Mock()

    antwoorden = iter([input_value, "0.24"])

    prompt_mock = Mock()
    prompt_mock.execute.side_effect = lambda: next(antwoorden)

    text_mock = Mock(return_value=prompt_mock)

    monkeypatch.setattr(
        "InquirerPy.inquirer.text",
        text_mock,
    )

    append_mock = Mock()
    monkeypatch.setattr(
        "geoprob_pipe.cmd_app.general.traject_parameters._append_to_db",
        append_mock,
    )

    _specify_w(app_settings)

    captured = capsys.readouterr()

    # juiste foutmelding getoond
    assert verwachte_tekst in captured.out

    # eerst fout, daarna geldige invoer
    assert prompt_mock.execute.call_count == 2

    # waarde opgeslagen
    append_mock.assert_called_once_with(
        app_settings=app_settings,
        key="w",
        value=0.24,
    )
