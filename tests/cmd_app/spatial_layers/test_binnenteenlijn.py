"""
Unit tests for `geoprob_pipe.cmd_app.spatial_layers.binnenteenlijn.py`.
Tests performed for:
    - added_binnenteenlijn(app_settings: ApplicationSettings) -> bool
"""

from unittest.mock import Mock

import geoprob_pipe.cmd_app.spatial_layers.binnenteenlijn as module


# --- added_binnenteenlijn(app_settings: ApplicationSettings) -> bool ---
def test_added_binnenteenlijn_already_included(
    monkeypatch,
    capsys,
) -> None:
    """Test case `binnenteenlijn` already added to gpkg."""
    # Arrange
    # Mock input arguments
    app_settings = Mock()
    app_settings.geopackage_filepath = "dummy.gpkg"

    # Monkey patch assigned function calls
    monkeypatch.setattr(
        module.fiona,
        "listlayers",
        Mock(return_value=[
            "trajectlijn",
            "binnenteenlijn",
            "vakindeling",
        ]),
    )

    # Mock called module fuctions
    request_mock = Mock()
    monkeypatch.setattr(
        module,
        "request_binnenteenlijn_filepath",
        request_mock,
    )

    # Act
    # Run tested function:
    result: bool = module.added_binnenteenlijn(app_settings)

    # Assert
    # Check expected return
    assert result is True

    # Check correct message printed
    captured = capsys.readouterr()
    assert "Binnenteenlijn al toegevoegd" in captured.out
    
    # Check function in other branch not called
    request_mock.assert_not_called()

    
    
def test_added_binnenteenlijn_not_yet_included(
    monkeypatch,
) -> None:
    """Test case `binnenteenlijn` not yet added to gpkg."""
    # Arrange
    # Mock input argument(s)
    app_settings = Mock()
    app_settings.geopackage_filepath = "dummy.gpkg"

    # Monkey patch assigned function call(s)
    monkeypatch.setattr(
        module.fiona,
        "listlayers",
        Mock(return_value=[
            "trajectlijn",
            "vakindeling",
        ]),
    )

    # Mock called module fuction(s)
    request_mock = Mock()
    monkeypatch.setattr(
        module,
        "request_binnenteenlijn_filepath",
        request_mock,
    )

    # Act
    # Run tested function:
    result: bool = module.added_binnenteenlijn(app_settings)

    # Assert
    # Check expected return
    assert result is True

    # Check function call with correct argument
    request_mock.assert_called_once_with(
        app_settings=app_settings
    )