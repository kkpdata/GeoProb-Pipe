from unittest.mock import Mock

import pytest

import geoprob_pipe.cmd_app.general.project as module


@pytest.mark.parametrize(
    "choice,function_name",
    [
        (
            "Bestaand project openen",
            "specify_path_to_existing_project",
        ),
        (
            "Nieuw project starten",
            "specify_dir_for_new_project",
        ),
    ]
)
def test_created_project_happy_paths(
    monkeypatch,
    choice,
    function_name,
):
    app_settings = Mock()

    prompt_mock = Mock()
    prompt_mock.execute.return_value = choice

    monkeypatch.setattr(
        "InquirerPy.inquirer.select",
        Mock(return_value=prompt_mock)
    )

    action_mock = Mock()
    logging_mock = Mock()

    monkeypatch.setattr(
        module,
        function_name,
        action_mock,
    )

    monkeypatch.setattr(
        module,
        "enable_geopackage_logging",
        logging_mock,
    )

    result = module.created_project(app_settings)

    assert result is True

    action_mock.assert_called_once_with(app_settings)

    logging_mock.assert_called_once_with(
        app_settings=app_settings
    )
    

def test_created_project_compare(monkeypatch):
    prompt_mock = Mock()
    prompt_mock.execute.return_value = (
        "Twee projectbestanden vergelijken"
    )

    monkeypatch.setattr(
        "InquirerPy.inquirer.select",
        Mock(return_value=prompt_mock)
    )

    compare_mock = Mock()
    monkeypatch.setattr(
        module,
        "start_comparison",
        compare_mock
    )

    with pytest.raises(SystemExit, match="Applicatie afgesloten"):
        module.created_project(Mock())

    compare_mock.assert_called_once()