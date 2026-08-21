"""
Unit tests for `geoprob_pipe.cmd_app.general.project.py`.
Tests performed for:
    - created_project(app_settings: ApplicationSettings) -> bool
"""

from unittest.mock import Mock

import pytest

import geoprob_pipe.cmd_app.general.project as module


# --- created_project(app_settings: ApplicationSettings) -> bool ---
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
    ],
)
def test_created_project_happy_paths(
    monkeypatch,
    choice: str,
    function_name: str,
) -> None:
    """Test of the paths are correctly completed."""
    # Mock input arguments
    app_settings = Mock()

    # Mock assigned function calls
    prompt_mock = Mock()
    prompt_mock.execute.return_value = choice

    monkeypatch.setattr("InquirerPy.inquirer.select", Mock(return_value=prompt_mock))

    # Mock called functions
    action_mock = Mock()
    monkeypatch.setattr(
        module,
        function_name,
        action_mock,
    )
    logging_mock = Mock()
    monkeypatch.setattr(
        module,
        "enable_geopackage_logging",
        logging_mock,
    )

    result: bool = module.created_project(app_settings)

    # Check path reaches return
    assert result is True

    # Check functions were called once with correct arguments
    action_mock.assert_called_once_with(app_settings)

    logging_mock.assert_called_once_with(app_settings=app_settings)


def test_created_project_compare(monkeypatch) -> None:
    """ "Test start compare function."""
    # Mock assigned function calls
    prompt_mock = Mock()
    choice: str = "Twee projectbestanden vergelijken"
    prompt_mock.execute.return_value = choice
    monkeypatch.setattr("InquirerPy.inquirer.select", Mock(return_value=prompt_mock))

    # Mock called functions
    compare_mock = Mock()
    monkeypatch.setattr(module, "start_comparison", compare_mock)

    # While capturing the sysexit() run the function
    with pytest.raises(SystemExit, match="Applicatie afgesloten"):
        module.created_project(Mock())

    # Check function call
    compare_mock.assert_called_once()


def test_created_project_single_calc(monkeypatch) -> None:
    # Mock assigned function calls
    prompt_mock = Mock()
    choice: str = "Inspecteer een enkele berekening"
    prompt_mock.execute.return_value = choice
    monkeypatch.setattr("InquirerPy.inquirer.select", Mock(return_value=prompt_mock))

    # Mock called functions
    panel_instance = Mock()
    panel_mock = Mock(return_value=panel_instance)
    monkeypatch.setattr(
        module,
        "Panel",
        panel_mock,
    )
    console_instance = Mock()
    console_mock = Mock(return_value=console_instance)
    monkeypatch.setattr(
        module,
        "Console",
        console_mock,
    )
    # While capturing the sysexit() run the function
    with pytest.raises(SystemExit, match="Applicatie afgesloten"):
        module.created_project(Mock())

    # Check Panel construction
    panel_mock.assert_called_once_with(
        module.EXPLANATION_REPRODUCING_SINGLE_CALCULATION,
        title="INSPECTEER EEN ENKELE BEREKENING",
        title_align="left",
        border_style="bright_blue",
        padding=(0, 2),
    )
    # Check print call
    console_instance.print.assert_called_once_with(panel_instance)
